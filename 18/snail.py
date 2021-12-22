from functools import partial
from itertools import starmap
import sys
import typing as ty
from dataclasses import dataclass, field
import re
import unittest
from abc import ABC, abstractmethod

@dataclass
class Node(ABC):
    parent: ty.Optional['Node'] = field(repr=False)

    @abstractmethod
    def _format_iter(self): ...
    @abstractmethod
    def magnitude(self) -> int: ...

@dataclass
class Leaf(Node):
    value: int
    def _format_iter(self):
        yield str(self.value)
    def magnitude(self):
        return self.value

@dataclass
class Pair(Node):
    left: Node
    right: Node
    def __post_init__(self):
        self.left.parent = self
        self.right.parent = self
    def _format_iter(self):
        yield '['
        yield from self.left._format_iter()
        yield ','
        yield from self.right._format_iter()
        yield ']'
    def magnitude(self):
        return 3 * self.left.magnitude() + 2 * self.right.magnitude()

def format_pair(r: Node, sep=" ") -> str:
    return sep.join(r._format_iter())

def parse_pairs(s: str) -> Pair:
    tokens = re.split(r'(\[|\]|,| +)', s)
    stack = []

    for tk in tokens:    
        if tk == '':
            continue
        elif tk == "[":
            continue
        elif tk == ",":
            continue
        elif tk.isspace():
            continue
        elif tk == "]":
            right = stack.pop()
            left = stack.pop()
            stack.append(Pair(None, left, right))
        else:
            stack.append(Leaf(None, int(tk)))

    assert len(stack) == 1
    return stack[0]

def first_split(r: Node) -> Leaf:
    s = inorder_traversal(r)
    s = starmap(lambda _, r: r, s)
    s = filter(lambda r: isinstance(r, Leaf), s)
    s = filter(lambda r: r.value >= 10, s)
    return next(s, None)

def split_node(n: Leaf):
    def to_pair(n: int) -> Pair:
        return Pair(
            None,
            Leaf(None, n // 2),
            Leaf(None, (n + 1) // 2))

    p = n.parent
    new = to_pair(n.value)
    new.parent = p

    if p.left == n:
        p.left = new
    else:
        p.right = new 

def star(f): return lambda t: f(*t)
def flip(f): return lambda *t: f(*reversed(t))

def inorder_traversal(r: Node, withleaves=True, depth=0) -> Node | None:
    if isinstance(r, Leaf):
        if withleaves:
            yield depth, r
        return
    
    assert isinstance(r, Pair)
    yield from inorder_traversal(r.left, withleaves, depth+1)
    yield depth, r
    yield from inorder_traversal(r.right, withleaves, depth+1)

def first_exploder(
    r: Node,
    depth: int = None
) -> tuple[ Leaf | None, Pair, Leaf | None ]:
    left, exploder, right = None, None, None
    isleaf = partial(flip(isinstance), Leaf)

    if depth is None:
        depth = 4

    def explodable(d, n):
        return (
            d == depth and
            isleaf(node.left) and
            isleaf(node.right)
        )

    s = inorder_traversal(r, withleaves=False)
    for d, node in s:
        assert not isleaf(node)
        if explodable(d, node):
            exploder = node
            break
        if isleaf(node.right):
            left = node.right
        elif isleaf(node.left):
            left = node.left

    if exploder is None:
        return None, None, None

    for _, node in s:
        if isleaf(node.left):
            right = node.left
            break
        elif isleaf(node.right):
            right = node.right
            break
    
    return left, exploder, right

def explode_node(left: Leaf | None, node: Pair, right: Leaf | None):
    if left:
        left.value += node.left.value
    if right:
        right.value += node.right.value
    
    parent = node.parent
    if parent.left == node:
        parent.left = Leaf(parent, 0)
    elif parent.right == node:
        parent.right = Leaf(parent, 0)
    else:
        assert False, f'neither left nor right? {parent=} {node=}'

def try_explode(n: Pair) -> bool:
    left, node, right = first_exploder(n)
    if not node:
        return False
    explode_node(left, node, right)
    return True

def try_split(n: Pair) -> bool:
    node = first_split(n)
    if not node:
        return False
    split_node(node)
    return True
        
def part1(fname: str):
    pass

if __name__ == '__main__':
    part1(sys.argv[1])
    sys.exit(0)

class MagnitudeTests(unittest.TestCase):
    def test_leaf(self):
        node = Leaf(None, 7)
        self.assertEqual(7, node.magnitude())
    def test_pair91(self):
        node = Pair(None, Leaf(None, 9), Leaf(None, 1))
        self.assertEqual(29, node.magnitude())
    def test_pair19(self):
        node = Pair(None, Leaf(None, 1), Leaf(None, 9))
        self.assertEqual(21, node.magnitude())
    def test_example_magnitudes(self):
        examples = [
            ([[1,2],[[3,4],5]], 143),
            ([[[[0,7],4],[[7,8],[6,0]]],[8,1]], 1384),
            ([[[[1,1],[2,2]],[3,3]],[4,4]], 445),
            ([[[[3,0],[5,3]],[4,4]],[5,5]], 791),
            ([[[[5,0],[7,4]],[5,5]],[6,6]], 1137),
            ([[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]], 3488),
        ]
        for input, expected in examples:
            node = parse_pairs(str(input))
            self.assertEqual(expected, node.magnitude())

class ReductionTests(unittest.TestCase):
    def test_reduction_example(self):
        orig = [[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]
        final = [[[[0,7],4],[[7,8],[6,0]]],[8,1]]

        num = parse_pairs(str(orig))
        final = parse_pairs(str(final))

        while try_explode(num) or try_split(num):
            pass
        
        self.assertEqual(format_pair(final, sep=""), format_pair(num, sep="")) 
    
class ExplodeNodeTests(unittest.TestCase):
    def test_explode(self):
        examples = [
            (1, [[2, 3], 3], [0, 6]),
            (1, [6, [2, 3]], [8, 0]),
            (2, [[6, [2, 3]], 11], [[8, 0], 14]),
            
            # from problems text

            (None, [[[[[9,8],1],2],3],4], [[[[0,9],2],3],4]),
            (None, [7,[6,[5,[4,[3,2]]]]], [7,[6,[5,[7,0]]]]),
            (None, [[6,[5,[4,[3,2]]]],1], [[6,[5,[7,0]]],3]),
            (None, [[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]], [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]),
            (None, [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]], [[3,[2,[8,0]]],[9,[5,[7,0]]]]),
        ]
        for depth, input, expected in examples:
            num = parse_pairs(str(input))
            exp = format_pair(parse_pairs(str(expected)), sep="")

            left, node, right = first_exploder(num, depth=depth)
            self.assertIsNotNone(node)
            explode_node(left, node, right)

            self.assertEqual(exp, format_pair(num, sep="")) 

class FirstExploderTests(unittest.TestCase):
    def test_no_exploder_in_single_leaf(self):
        r = parse_pairs("5")
        left, exploder, right = first_exploder(r)
        self.assertIsNone(left)
        self.assertIsNone(exploder)
        self.assertIsNone(right)
    def test_find_depth0_exploder(self):
        r = parse_pairs("[2,3]")
        left, exploder, right = first_exploder(r, 0)
        self.assertEqual(r, exploder)
        self.assertIsNone(left)
        self.assertIsNone(right)
    def test_find_depth1_exploder(self):
        r = parse_pairs('[[1, 2], 3]')
        _, exploder, _ = first_exploder(r, depth=1)
        self.assertEqual(r.left, exploder)
    def test_find_only_at_requested_depth(self):
        r = parse_pairs('[ [ [1, 2], [3, 4] ], [ 5, 6] ]')
        _, exploder, _ = first_exploder(r, depth=1)
        self.assertEqual(5, exploder.left.value)
        self.assertEqual(6, exploder.right.value)
    def test_find_exploder_ex1(self):
        r = parse_pairs("[[6,[5,[4,[3,2]]]],1]")
        _, exploder, _ = first_exploder(r)
        self.assertEqual(3, exploder.left.value)
        self.assertEqual(2, exploder.right.value)
    def test_find_exploder_ex2(self):
        r = parse_pairs("[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]")
        _, exploder, _ = first_exploder(r)
        self.assertEqual(7, exploder.left.value)
        self.assertEqual(3, exploder.right.value)
    def test_correct_predecessor(self):
        examples = [
            (1, "[1, 2]", None),
            (1, "[1, [2, 3]]", 1),
            (2, "[0, [7, [2, 3]]]", 7),
            (None, "[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]", 1),
            (1, "[[1, [2, 3]], [4,5]]", 3),
            (1, "[[[0, 1], [2, 3]], [4,5]]", 3)
        ]
        for depth, s, expected in examples:
            left, _, _ = first_exploder(parse_pairs(s), depth=depth)
            if expected is None:
                self.assertIsNone(left, s)
            else:
                self.assertIsNotNone(left, s)
                self.assertEqual(expected, left.value, s)
    def test_correct_successor(self):
        examples = [
            (1, "[1, 2]", None),
            (1, "[[2, 3], 4]", 4),
            (2, "[0, [7, [2, 3]]]", None),
            (2, "[0, [[2, 3], 7]]", 7),
            (None, "[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]", 6),
            (2, "[[1, [2, 3]], [4,5]]", 4),
            (1, "[[4,5], [[0, 1], [2, 3]]]", 0)
        ]
        for depth, s, expected in examples:
            _, _, right = first_exploder(parse_pairs(s), depth=depth)
            if expected is None:
                self.assertIsNone(right, s)
            else:
                self.assertIsNotNone(right, s)
                self.assertEqual(expected, right.value, s)
        
class SplitTests(unittest.TestCase):
    def test_find_simple_split_on_the_left(self):
        p = parse_pairs('[10,0]')
        self.assertEqual(
            p.left, 
            first_split(p)
        )
    def test_find_simple_split_on_the_right(self):
        p = parse_pairs('[0,10]')
        self.assertEqual(
            p.right,
            first_split(p)
        )
    def test_simple_split(self):
        p = parse_pairs("[10,0]")
        split_node(first_split(p))
        self.assertEqual(
            "[[5,5],0]",
            format_pair(p, "")
        )
    def test_interior_split_a(self):
        p = parse_pairs('[[0,10],[0,0]]')
        split_node(first_split(p))
        self.assertEqual(
            '[[0,[5,5]],[0,0]]',
            format_pair(p, "")
        )
    def test_interior_split_b(self):
        p = parse_pairs('[[0,0],[10,0]]')
        split_node(first_split(p))
        self.assertEqual(
            '[[0,0],[[5,5],0]]',
            format_pair(p, "")
        )
    def test_find_correct_split(self):
        p = parse_pairs('[[0,10],[10,0]]')
        split_node(first_split(p))
        self.assertEqual(
            '[[0,[5,5]],[10,0]]',
            format_pair(p, "")
        )

class ParserTests(unittest.TestCase):
    def test_integer(self):
        result = parse_pairs("5")
        assert isinstance(result, Leaf)
        assert result.value == 5
    def test_simple_pair(self):
        p = parse_pairs("[3,5]")
        assert p.left.value == 3
        assert p.right.value == 5
    def test_simple_nested(self):
        p = parse_pairs("[[3,5],[1,2]]")
        assert isinstance(p, Pair)
        assert isinstance(p.left, Pair)
        assert isinstance(p.right, Pair)
        assert p.left.left.value == 3
        assert p.left.right.value == 5
        assert p.right.left.value == 1
        assert p.right.right.value == 2

class FormatTests(unittest.TestCase):
    def test_simple_pair(self):
        p = parse_pairs("[3,5]")
        s = format_pair(p)
        assert s == "[ 3 , 5 ]", f'<{s}>'