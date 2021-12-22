import numpy as np
from enum import Enum, auto
import sys
import re
from dataclasses import dataclass
from typing import NamedTuple

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

    def contains(self, other: 'Cuboid'):
        return (
            self.xb.contains(other.xb) and
            self.yb.contains(other.yb) and
            self.zb.contains(other.zb)
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

if __name__ == '__main__':
    part1(sys.argv[1])
    # part2(sys.argv[1])
    exit(0)