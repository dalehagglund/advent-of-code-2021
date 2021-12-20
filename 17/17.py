import itertools
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import reduce, partial
from itertools import islice
from typing import NamedTuple
# import numpy as np
import math

@dataclass(frozen=True)
class Box:
    xmin: int
    xmax: int
    ymin: int
    ymax: int

class Pos(NamedTuple):
    x: int
    y: int
    def hits(self, b: Box) -> bool:
        return (
            b.xmin <= self.x <= b.xmax and
            b.ymin <= self.y <= b.ymax
        )
    def overshoots(self, b: Box) -> bool:
        return (self.y < b.ymin or self.x > b.xmax)

class Vel(NamedTuple):
    dx: int
    dy: int
    def magnitude(self):
        return math.sqrt(self.dx ** 2 + self.dy ** 2)
    def trajectory(self):
        dx, dy = self.dx, self.dy
        x, y = 0, 0
        while True:
            yield Pos(x, y)
            x, y = x + dx, y + dy
            dx, dy = max(0, dx - 1), dy - 1

def grid_velocities(xmin, xmax, ymin, ymax):
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            yield Vel(x, y)

def zigzag_velocities():
    vx, vy = 0, 0
    xstep, ystep = -1, +1
    while True:
        yield Vel(vx, vy)
        if vx + xstep < 0:
            vx, vy = 0, vy + 1
            xstep, ystep = +1, -1
        elif vy + ystep < 0:
            vx, vy = vx + 1, 0
            xstep, ystep = -1, +1
        else:
            vx, vy = vx + xstep, vy + ystep

def read_input(fname: str) -> Box:
    with open(fname) as f:
        line = next(f).strip()
        _, _, xdef, ydef = line.split()
        xmin, xmax = map(int, xdef[2:-1].split(".."))
        ymin, ymax = map(int, ydef[2:].split(".."))
        return Box(xmin, xmax, ymin, ymax)

def simulate(b: Box, v: Vel):
    maxy = float('-inf')
    for pos in v.trajectory():
        maxy = max(pos.y, maxy)
        if pos.hits(b):
            return True, v, maxy
        elif pos.overshoots(b):
            return False, None, None
    assert False, "{box = } {v = } should either hit or overshoot"

def star(f): return lambda t: f(*t)
def drain(s):
    for _ in s:
        pass

def every(f, n, s):
    count = 0
    for item in s:
        count += 1
        if count % n == 0:
            f(count, item)
        yield item

def observe(f, s):
    for item in s:
        f(item)
        yield item

def part1(fname: str):
    print("===== part 1")
    box = read_input(fname)
    hitcount = 0
    print(f'{box}')
    def inc_hitcount(*args):
        nonlocal hitcount
        hitcount += 1

    s = grid_velocities(0, box.xmax + 1, box.ymin, -box.ymin + 1)
    # s = every(partial(print, '... n:'), 500, s)

    s = map(partial(simulate, box), s)
    s = filter(star(lambda hit, _x, _y: hit), s)
    s = map(star(lambda _, vel, height: (vel, height)), s)
    s = every(partial(print, "... hit:"), 25, s)
    s = observe(inc_hitcount, s)

    s = map(star(lambda _, ht: ht), s)
    print(f'part 1: max height {max(s)}')
    print(f'part 2: total velocities {hitcount}')

if __name__ == '__main__':
    part1(sys.argv[1])