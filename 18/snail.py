from functools import partial
from itertools import starmap
import sys
import typing as ty
from dataclasses import dataclass
import re
import unittest
from abc import ABC, abstractmethod

@dataclass
class Node(ABC):
    parent: ty.Union['Node', None]

    @abstractmethod
    def _format_iter(self): ...

@dataclass
class Leaf(Node):
    value: int
    def _format_iter(self):
        yield str(self.value)

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

def format_pair(r: Node, sep=" ") -> str:
    return sep.join(r._format_iter())

def parse_pairs(s: str) -> Pair:
    tokens = re.split(r'(\[|\]|, *)', s)
    stack = []

    for tk in tokens:    
        if tk == '':
            continue
        elif tk == "[":
            continue
        elif tk == ",":
            continue
        elif tk == "]":
            right = stack.pop()
            left = stack.pop()
            stack.append(Pair(None, left, right))
        else:
            stack.append(Leaf(None, int(tk)))

    assert len(stack) == 1
    return stack[0]

def find_leftmost_split(r: Node) -> Leaf:
    s = walk_inorder(r)
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

def part1(fname: str):
    pass

if __name__ == '__main__':
    part1(sys.argv[1])
    sys.exit(0)

def star(f): return lambda t: f(*t)
def flip(f): return lambda t: f(*reversed(t))

def walk_inorder(r: Node, depth=0) -> Node | None:
    if isinstance(r, Pair):
        yield from walk_inorder(r.left, depth+1)
    yield depth, r
    if isinstance(r, Pair):
        yield from walk_inorder(r.right, depth+1)

def find_leftmost_exploding(
    r: Node,
    depth: int = 4
) -> tuple[ Leaf | None, Pair, Leaf | None ]:
    prev, pair, next = None, None, None

    isleaf = partial(flip(isinstance), Leaf)

    s = walk_inorder(r)
    for nodedepth, node in s:
        if isinstance(node, Leaf):
            prev = node
            continue
        if nodedepth == depth and isleaf(node.left) and isleaf(node.right):
            pair = node
            break

    if pair is None:
        return None, None, None

    for _, node in s:
        if isinstance(node, Leaf):
            next = node
            break
    
    return prev, pair, next


class SplitTests(unittest.TestCase):
    def test_find_simple_split_on_the_left(self):
        p = parse_pairs('[10,0]')
        self.assertEqual(
            p.left, 
            find_leftmost_split(p)
        )
    def test_find_simple_split_on_the_right(self):
        p = parse_pairs('[0,10]')
        self.assertEqual(
            p.right,
            find_leftmost_split(p)
        )
    def test_simple_split(self):
        p = parse_pairs("[10,0]")
        split_node(find_leftmost_split(p))
        self.assertEqual(
            "[[5,5],0]",
            format_pair(p, "")
        )
    def test_interior_split_a(self):
        p = parse_pairs('[[0,10],[0,0]]')
        split_node(find_leftmost_split(p))
        self.assertEqual(
            '[[0,[5,5]],[0,0]]',
            format_pair(p, "")
        )
    def test_interior_split_b(self):
        p = parse_pairs('[[0,0],[10,0]]')
        split_node(find_leftmost_split(p))
        self.assertEqual(
            '[[0,0],[[5,5],0]]',
            format_pair(p, "")
        )
    def test_find_correct_split(self):
        p = parse_pairs('[[0,10],[10,0]]')
        split_node(find_leftmost_split(p))
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