from functools import partial, reduce
import numpy as np
from enum import Enum, auto
import sys
import re
from dataclasses import dataclass
from typing import NamedTuple
from itertools import islice, product
import unittest
import typing as ty
import abc

np.seterr(all='raise')

# closed integer interval
class Bounds(NamedTuple):
    min: int
    max: int

    def length(self):
        return self.max - self.min + 1
    def contains(self, other: 'Bounds') -> bool:
        smin, smax = self.min, self.max
        return (
            smin <= other.min <= smax and
            smin <= other.max <= other.max
        )
    def extend_to(self, other: 'Bounds') -> 'Bounds':
        return Bounds(
            min(self.min, other.min),
            max(self.max, other.max)
        )
    def split(self) -> tuple['Bounds' ,'Bounds']:
        mid = (self.max + self.min) // 2
        return Bounds(self.min, mid), Bounds(mid + 1, self.max)
    def intersection(self, other: 'Bounds') -> ty.Optional['Bounds']:
        omin, omax = other

        if omax < self.min: return None     # other to the left of self
        if self.max < omin: return None     # other to the right of self

        if omin <= self.min and self.max <= omax:
            # other extends past both ends of self
            return self
        elif omin < self.min and self.has(omax):
            # other overlaps overlaps left end of self
            return Bounds(self.min, omax)
        elif self.has(omin) and self.max < omax:
            # other overlaps right end of self
            return Bounds(omin, self.max)
        elif self.has(omin) and self.has(omax):
            # other fully within self
            return other
        else:
            assert False, "huh? no case matches!"
    def has(self, n: int) -> bool:
        return self.min <= n <= self.max

@dataclass(frozen=True)
class Cuboid:
    xb: Bounds
    yb: Bounds
    zb: Bounds

    def __post_init__(self):
        assert self.xb.min <= self.xb.max
        assert self.yb.min <= self.yb.max
        assert self.zb.min <= self.zb.max

    @classmethod
    def from_bounds(cls, xmin, xmax, ymin, ymax, zmin, zmax):
        return cls(
            Bounds(xmin,xmax),
            Bounds(ymin,ymax),
            Bounds(zmin,zmax),
        )
    def intersection(self, other: 'Cuboid') -> ty.Optional['Cuboid']:
        xb = self.xb.intersection(other.xb)
        yb = self.yb.intersection(other.yb)
        zb = self.zb.intersection(other.zb)
        if not xb or not yb or not zb:
            return None
        return Cuboid(xb, yb, zb)
    def split(self) -> list['Cuboid']:
        xbs = self.xb.split()
        ybs = self.yb.split()
        zbs = self.zb.split()
        return [
            Cuboid(xb, yb, zb)
            for xb, yb, zb
            in product(xbs, ybs, zbs)
        ]
    def contains(self, other: 'Cuboid'):
        return (
            self.xb.contains(other.xb) and
            self.yb.contains(other.yb) and
            self.zb.contains(other.zb)
        )
    def extend_to(self, other: 'Cuboid') -> 'Cuboid':
        return Cuboid(
            self.xb.extend_to(other.xb),
            self.yb.extend_to(other.yb),
            self.zb.extend_to(other.zb)
        )
    def volume(self) -> int:
        return (
            self.xb.length() * self.yb.length() * self.zb.length()
        )
    def shape(self):
        return (
            self.xb.length(),
            self.yb.length(),
            self.zb.length()
        )
    def __str__(self):
        return "".join([
            'Cuboid(',
            "..".join(str(b) for b in self.xb),
            ", ",
            "..".join(str(b) for b in self.yb),
            ", ",
            "..".join(str(b) for b in self.zb),
            ')'
        ])

class State(Enum):
    ON = 1
    OFF = 0

def read_input(fname:str) -> list[tuple[State, Cuboid]]:
    state = {
        "on": State.ON,
        "off": State.OFF,
    } 

    def decode_line(line: str) -> tuple[State, Cuboid]:
        line = line.strip()
        line = re.sub(r'[xyz]=', '', line)
        toggle, x, y, z = re.split(r'[, ]', line)
        xbounds = Bounds(*map(int, x.split("..")))
        ybounds = Bounds(*map(int, y.split("..")))
        zbounds = Bounds(*map(int, z.split("..")))

        return (state[toggle], Cuboid(xbounds, ybounds, zbounds))

    with open(fname) as f:
        return [ decode_line(line) for line in f ]

class CubeTree(abc.ABC):
    @abc.abstractmethod
    def set(self, region: Cuboid, state: State): ...

    @abc.abstractmethod
    def box(self) -> Cuboid: ...

    @abc.abstractmethod
    def on_count(self) -> int: ...

    @abc.abstractmethod
    def off_count(self) -> int: ...

    @abc.abstractmethod
    def maxheight(self) -> int: ...

    @abc.abstractmethod
    def minheight(self) -> int: ...

    @abc.abstractmethod
    def nodecount(self) -> int: ...

class CubeLeaf(CubeTree):
    def __init__(self, box: Cuboid, lit: bool = False):
        self._box = box
        self._mat = np.full(
            box.shape(),
            dtype=np.bool8,
            fill_value = 1 if lit else 0
        ) 
        self._update_oncount()
    def on_count(self):
        return self._oncount
    def off_count(self):
        return self._box.volume() - self._oncount
    def maxheight(self):
        return 1
    def minheight(self):
        return 1
    def nodecount(self):
        return 1
    def box(self):
        return self._box
    def visit(self, visitor, depth=0):
        visitor('leaf', self, depth)
    def set(self, region: Cuboid, state: State):
        assert self._box.contains(region)

        imin = region.xb.min - self._box.xb.min
        imax = region.xb.max - self._box.xb.min + 1
        jmin = region.yb.min - self._box.yb.min
        jmax = region.yb.max - self._box.yb.min + 1
        kmin = region.zb.min - self._box.zb.min
        kmax = region.zb.max - self._box.zb.min + 1

        self._mat[imin : imax, jmin : jmax, kmin : kmax ] = state.value
        self._update_oncount()
    def _update_oncount(self):
        self._oncount = int(np.sum(self._mat, dtype=np.int32))

def part1(fname: str):
    core = CubeLeaf(
        Cuboid.from_bounds(-50, 50, -50, 50, -50, 50)
    )
    instrs = read_input(fname)
    for toggle, cube in instrs:
        if not core.box().contains(cube):
            continue
        core.set(cube, toggle)
    print(f'part 1: lit {core.on_count()}')

class CubeNode(CubeTree):
    # use a leaf node if an child would have
    # a dimension smaller than this.
    MIN_DIMENSION = 20

    def __init__(self, box: Cuboid, lit: bool = False):
        self._box = box
        self._expanded = False
        self._children: list['CubeNode'] = None
        self._oncount = self._box.volume() if lit else 0 

    def set(self, region: Cuboid, state: State):
        assert self._box.contains(region)

        if self._box == region and not self._expanded:
            self._oncount = [0, self._box.volume()][state.value]
        elif self._box == region and self._expanded:
            self._discard_children()
            self._oncount = [0, self._box.volume()][state.value]
        elif self._box != region and not self._expanded:
            self._expand_children()
            self._update_children(region, state)
            self._oncount = sum(c.on_count() for c in self._children)
        elif self._box != region and self._expanded:
            self._update_children(region, state)
            self._oncount = sum(c.on_count() for c in self._children)
        else:
            assert False, "huh? case analysis exhausted"
    
    def _discard_children(self):
        self._children = None
        self._expanded = False
    def _expand_children(self):
        assert not self._children
        assert self._oncount in [0, self._box.volume()]
        lit = self._oncount == self._box.volume()
        self._children = [
            self._make_child(subbox, lit)
            for subbox in self._box.split()
        ]
        self._expanded = True

    def _make_child(self, region, lit):
        min_side =  min(
            region.xb.length(),
            region.yb.length(),
            region.zb.length()
        )
        if min_side <= CubeNode.MIN_DIMENSION:
            factory = CubeLeaf
        else:
            factory = CubeNode
        return factory(region, lit=lit)

    def _update_children(self, region: Cuboid, state: State):
        for child in self._children:
            subregion = child._box.intersection(region)
            if not subregion:
                continue
            child.set(subregion, state)
    def box(self): return self._box
    def on_count(self): return self._oncount
    def off_count(self): return self._box.volume() - self._oncount
    def nodecount(self):
        if not self._expanded: return 1
        return 1 + sum(c.nodecount() for c in self._children)
    def minheight(self):
        if not self._expanded:
            return 1
        return 1 + min(c.minheight() for c in self._children)
    def maxheight(self):
        if not self._expanded:
            return 1
        return 1 + max(c.maxheight() for c in self._children)
    def visit(self, visitor, depth=0):
        visitor('before node', self, depth)
        if self._expanded:
            for c in self._children:
                c.visit(visitor, depth+1)
        visitor('after node', self, depth)

def flip(f): return lambda *args: f(*reversed(args))

def part2(fname: str):
    instrs = read_input(fname)
    cuboid = reduce(
        lambda c1, c2: c1.extend_to(c2),
        (inst[1] for inst in instrs))

    max_set = sum(c.volume() for toggle, c in instrs if toggle == State.ON)
    max_clear = sum(c.volume() for toggle, c in instrs if toggle == State.OFF)
    print('max cuboid', cuboid)
    print('volume', cuboid.volume())
    print('max cells set', max_set)
    print('max cells clear', max_set)
    print('max set density', max_set / cuboid.volume())
    print('max clear density', max_clear / cuboid.volume())

    if max(
        cuboid.xb.length(), 
        cuboid.yb.length(),
        cuboid.zb.length(),
    ) > CubeNode.MIN_DIMENSION:
        node = CubeNode(cuboid)
    else:
        node = CubeLeaf(cuboid)

    node = CubeNode(cuboid)

    for i, (toggle, cube) in enumerate(instrs):
        minh = node.minheight()
        maxh = node.maxheight()
        nc = node.nodecount()
        print(f'step {i} {nc = } {minh = } {maxh = } {toggle = } {cube = }')
        node.set(cube, toggle)
        

    print(f'part 2: total lit {node.on_count()}')
    return 

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])
    exit(0)

warn = partial(print, file=sys.stderr)

class BigTests(unittest.TestCase):
    def make_node(self, size):
        return CubeNode(
            Cuboid.from_bounds(
                -size, size,
                -size, size,
                -size, size
            ))
    def make_region(self, size):
        return Cuboid.from_bounds(
            -size, size,
            -size, size,
            -size, size
        )
    def test_tiny_region(self):
        warn('\ntiny')
        node =  self.make_node(1000)
        region = self.make_region(2)
        node.set(region, State.ON)
        minh = node.minheight()
        maxh = node.maxheight()
        count = node.nodecount()

        warn(f'{minh = } {maxh = } {count = }')
        self.assertEquals(region.volume(), node.on_count())
    def test_huge_region(self):
        warn('\nhuge')
        N = 1000
        node =  self.make_node(N)
        region = self.make_region(N - 50)
        node.set(region, State.ON)
        minh = node.minheight()
        maxh = node.maxheight()
        count = node.nodecount()
        @dataclass
        class Stats:
            total: int = 0
            inside: int = 0
            outside: int = 0
            edge: int = 0
            expanded: int = 0
        nstats = Stats()
        lstats = Stats()

        def visitor(tag, node, depth):
            if tag not in ['before node', 'leaf']:
                return

            intersection = region.intersection(node.box())
            inside = intersection == node.box()
            outside = intersection == None
            edge = intersection is not None and intersection != node.box()
            leaf = isinstance(node, CubeLeaf)

            expanded = node._expanded if not leaf else False

            if_ = ".I"[inside]
            of = '.O'[outside]
            ef = '.E'[edge]
            lf = '.L'[leaf]
            xf = ".X"[expanded]

            assert sum([inside, outside, edge]) == 1
            # if inside: assert not expanded
            # if outside: assert not expanded
            # if edge and not leaf: assert expanded

            bucket = lstats if leaf else nstats
                
            bucket.inside += inside
            bucket.outside += outside
            bucket.edge += edge
            bucket.expanded += expanded
            bucket.total += 1
            
            # if not leaf:
            #     warn(" >" * depth, "node", f'{lf}{if_}{ef}{of}{xf}', node.box())

        node.visit(visitor)

        warn(f'{region = }')
        warn(f'{minh = } {maxh = } {count = }')
        warn(f'{nstats = } {lstats = }')
        self.assertEquals(region.volume(), node.on_count())

class CubeNodeTests(unittest.TestCase):
    def make_node(self, *bounds):
        return CubeNode(Cuboid.from_bounds(*bounds))
    def test_new_node_unlit(self):
        cube = Cuboid.from_bounds(0, 127, 0, 127, 0, 127)
        node = CubeNode(cube)
        self.assertEqual(cube, node.box())
        self.assertEqual(0, node.on_count())
        self.assertEqual(cube.volume(), node.off_count())
    def test_new_node_lit(self):
        cube = Cuboid.from_bounds(0, 127, 0, 127, 0, 127)
        node = CubeNode(cube, lit=True)
        self.assertEqual(cube.volume(), node.on_count())
        self.assertEqual(0, node.off_count())
    def test_light_entire_cube(self):
        cube = Cuboid.from_bounds(0, 127, 0, 127, 0, 127)
        node = CubeNode(cube)
        node.set(cube, State.ON)
        self.assertEqual(cube.volume(), node.on_count())
        self.assertEqual(0, node.off_count())
    def test_small_expand(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        node._expand_children()
        self.assertTrue(node._expanded)
        self.assertEqual(8, len(node._children))
        for c in node._children:
            self.assertIsInstance(c, CubeLeaf)
        self.assertEqual(2, node.maxheight())
    def test_large_expand(self):
        node = self.make_node(0, 255, 0, 255, 0, 255)
        node._expand_children()
        self.assertTrue(node._expanded)
        self.assertEqual(8, len(node._children))
        for c in node._children:
            self.assertIsInstance(c, CubeNode)
        self.assertEqual(2, node.maxheight())
    def test_light_entire_subcube(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        subcube = node.box().split()[0]
        node.set(subcube, State.ON)
        self.assertEqual(subcube.volume(), node.on_count())
        self.assertEqual(2, node.maxheight())
    def test_entire_cube_on_then_off(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        node.set(node.box(), State.ON)
        node.set(node.box(), State.OFF)
        self.assertEqual(node.box().volume(), node.off_count())
        self.assertEqual(0, node.on_count())
        self.assertEqual(1, node.maxheight())
    def test_toggle_subcube_on_then_off(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        subcube = node.box().split()[0]
        node.set(subcube, State.ON)
        node.set(subcube, State.OFF)
        self.assertEqual(0, node.on_count())
        self.assertEqual(2, node.maxheight())
    def test_light_then_clear_subcube(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        subcube = node.box().split()[0]
        node.set(subcube, State.ON)
        node.set(subcube, State.OFF)
        self.assertEqual(0, node.on_count())
        self.assertEqual(2, node.maxheight())
    def test_light_two_subcubes(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        splits = node.box().split()
        sub1, sub2 = splits[0], splits[-1]
        node.set(sub1, State.ON)
        node.set(sub2, State.ON)
        self.assertEqual(sub1.volume() + sub2.volume(), node.on_count())
    def test_light_entire_cube_then_clear_subcube(self):
        node = self.make_node(0, 127, 0, 127, 0, 127)
        subcube = node.box().split()[0]
        node.set(node.box(), State.ON)
        node.set(subcube, State.OFF)
        self.assertEqual(node.box().volume() - subcube.volume(), node.on_count())

class CubeLeafTests(unittest.TestCase):
    def test_example_1(self):
        input = [
            (State.ON,  (10, 12, 10, 12, 10, 12)),
            (State.ON,  (11, 13, 11, 13, 11, 13)),
            (State.OFF, (9, 11, 9, 11, 9, 11)),
            (State.ON,  (10, 10, 10, 10, 10, 10)),
        ]
        node = CubeLeaf(
            Cuboid.from_bounds(-50, 50, -50, 50, -50, 50),
            lit=False
        )
        for state, bounds in input:
            node.set(
                Cuboid.from_bounds(*bounds),
                state
            )
        self.assertEqual(39, node.on_count())

class IntersectionTests(unittest.TestCase):
    def test_bounds_has(self):
        b = Bounds(0, 10)
        self.assertTrue(b.has(0))
        self.assertTrue(b.has(1))
        self.assertTrue(b.has(9))
        self.assertTrue(b.has(10))
        self.assertFalse(b.has(-1))
        self.assertFalse(b.has(11))
    
    def test_bounds_intersection(self):
        b = Bounds(0, 10)

        self.assertIsNone(b.intersection((-5, -1)))
        self.assertIsNone(b.intersection((11, 15)))

        self.assertEqual((0, 1), b.intersection((-1, 1)))
        self.assertEqual((2,5), b.intersection((2, 5)))
        self.assertEqual((7, 10), b.intersection((7,15)))

        self.assertEqual(b, b.intersection(b))
        self.assertEqual((0, 10), b.intersection((-15, 15)))

    def test_cuboid_full_overlap(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10) 
        b1 = Cuboid.from_bounds(3, 3, 3, 3, 3, 3)
        b2 = Cuboid.from_bounds(10, 10, 10, 10, 10, 10)

        self.assertEqual(cube, cube.intersection(cube))
        self.assertEqual(b1, cube.intersection(b1))
    
    def test_cuboid_with_larger(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10) 
        b3 = Cuboid.from_bounds(
            -20, 20,
            -20, 20,
            -20, 20
        )
        self.assertEqual(cube, cube.intersection(b3))

    def test_cuboid_partial_overlap(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10)
        examples = [
            [ (9, 11, 9, 11, 9, 11), (9, 10, 9, 10, 9, 10) ],
            [ (-1, 1, -1, 1, -1, 1), (0, 1, 0, 1, 0, 1) ],
        ]
        for i, (rbounds, expbounds) in enumerate(examples):
            region = Cuboid.from_bounds(*rbounds)
            expected = Cuboid.from_bounds(*expbounds)
            result = cube.intersection(region)
            self.assertEqual(expected, result, f'case {i}')

    def test_cuboid_no_overlap(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10)
        examples = [
            (11, 12, 11, 12, 11, 12),
            (-2, -1, -2, -1, -2, -1),
            (-2, -1, 3, 5, 3, 5),
            (0, 10, -2, -1, 0, 10),
            (2, 7, 2, 7, -2, -1),
        ]
        for i, rbounds in enumerate(examples):
            region = Cuboid.from_bounds(*rbounds)
            result = cube.intersection(region)
            self.assertIsNone(result, f'case {i}')


class SplitTests(unittest.TestCase):
    def test_bounds_splitting(self):
        b = Bounds(-10, 10)
        b1, b2 = b.split()

        self.assertEqual(b.length(), b1.length() + b2.length())
        self.assertTrue(0 <= abs(b1.length() - b2.length()) <= 1)
        self.assertEqual(b.min, b1.min)
        self.assertEqual(b.max, b2.max)
        self.assertEqual(b2.min, b1.max + 1)
        self.assertTrue(b.min < b1.max < b2.min < b.max)
    def test_cuboid_splitting(self):
        b = Bounds(0, 31)
        cube = Cuboid(b, b, b)
        splits = set(cube.split())
        self.assertEqual(8, len(splits))
        for expected in [
            ( 0, 15,  0, 15,  0, 15),
            ( 0, 15,  0, 15, 16, 31),
            ( 0, 15, 16, 31,  0, 15),
            ( 0, 15, 16, 31, 16, 31),
            (16, 31,  0, 15,  0, 15),
            (16, 31,  0, 15, 16, 31),
            (16, 31, 16, 31,  0, 15),
            (16, 31, 16, 31, 16, 31),
        ]:
            c = Cuboid.from_bounds(*expected)
            self.assertIn(c, splits)
            splits.remove(c)
        self.assertEqual(0, len(splits))