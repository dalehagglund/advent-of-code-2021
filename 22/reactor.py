from functools import reduce
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

def part1(fname: str):
    core = Cuboid.from_bounds(-50, 50, -50, 50, -50, 50)
    instrs = read_input(fname)

    mat = np.full(shape=core.shape(), fill_value=0, dtype=np.bool8)

    for toggle, cube in instrs:
        if not core.contains(cube):
            continue

        imin = cube.xb.min - core.xb.min
        imax = cube.xb.max - core.xb.min + 1

        jmin = cube.yb.min - core.yb.min
        jmax = cube.yb.max - core.yb.min + 1

        kmin = cube.zb.min - core.zb.min
        kmax = cube.zb.max - core.zb.min + 1

        mat[imin : imax, jmin : jmax, kmin : kmax ] = toggle.value

    count = np.sum(mat)
    print(f'part 1: lit {count}')

class CubeTree(abc.ABC):
    @abc.abstractmethod
    def switch_on(self, region: Cuboid): ...

    @abc.abstractmethod
    def box(self) -> Cuboid: ...

    @abc.abstractmethod
    def on_count(self) -> int: ...

    @abc.abstractmethod
    def off_count(self) -> int: ...

class CubeLeaf(CubeTree):
    pass

class CubeNode(CubeTree):
    def __init__(self, box: Cuboid, lit: bool = False):
        self._box = box
        self._expanded = False
        self._children: list['CubeNode'] = None
        self._oncount = self._box.volume() if lit else 0 

    def switch_on(self, region: Cuboid):
        assert self._box.contains(region)

        if self._box == region and not self._expanded:
            self._oncount = self._box.volume()
        elif self._box == region and self._expanded:
            self._discard_children()
            self._oncount  = self._box.volume()
        elif self._box != region and not self._expanded:
            self._expand_children()
            self._update_children(region)
            self._oncount = sum(c.on_count() for c in self._children)
        elif self._box != region and self._expanded:
            self._update_children(region)
            self._oncount = sum(c.on_count() for c in self._children)
        else:
            assert False, "huh? case analysis exhausted"
    
    def _discard_children(self):
        self._children = None
        self._expanded = False
    def _expand_children(self):
        self._children = [
            CubeNode(subbox, False)
            for subbox in self._box.split()
        ]
        self._expanded = True
    def _update_children(self, region: Cuboid):
        for child in self._children:
            subregion = child._box.intersect(region)
            if not subregion:
                continue
            child.switch_on(subregion)

    def box(self): return self._box
    def on_count(self): return self._oncount
    def off_count(self): return self._box.volume() - self._oncount


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
    return 

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])
    exit(0)

class CubeNodeTests(unittest.TestCase):
    def test_new_node_unlit(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10)
        node = CubeNode(cube)
        self.assertEqual(cube, node.box())
        self.assertEqual(0, node.on_count())
        self.assertEqual(cube.volume(), node.off_count())
    def test_new_node_lit(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10)
        node = CubeNode(cube, lit=True)
        self.assertEqual(cube.volume(), node.on_count())
        self.assertEqual(0, node.off_count())
    def test_light_entire_cube(self):
        cube = Cuboid.from_bounds(0, 10, 0, 10, 0, 10)
        node = CubeNode(cube)
        node.switch_on(cube)
        self.assertEqual(cube.volume(), node.on_count())

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
    # def test_cuboid_splitting(self):
    #     b = Bounds(0, 31)
    #     cube = Cuboid(b, b, b)
    #     for c in cube.split():
    #         print(c)