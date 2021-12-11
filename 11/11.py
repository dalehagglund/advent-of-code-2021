import sys
import numpy as np
import itertools
from collections import deque
import typing as ty

def read_array(fname):
    with open(fname) as f:
        grid = [
            list(map(int, line.strip()))
            for line in f
        ]
    return np.array(grid, dtype=np.int32)
    # return len(grid), len(grid[0]), grid

def star(f):
    return lambda t: f(*t)

def tap(f, s):
    for item in s:
        f(s)
        yield item

def neighbours(grid, row, col):
    nrow, ncol = grid.shape
    s = itertools.product([ -1, 0, +1 ], repeat=2)
    s = itertools.filterfalse(star(lambda dr, dc: dr == 0 and dc == 0), s)
    s = map(star(lambda dr, dc: (row + dr, col + dc)), s)
    s = filter(star(lambda r, c: 0 <= r < nrow and 0 <= c < ncol), s)
    return s

def step(grid):
    flashed = np.zeros(grid.shape, dtype=np.bool8)

    grid += 1
    while np.any(grid > 9):
        inc = np.zeros(grid.shape, dtype=np.int32)
        toflash = grid > 9
        for r, c in np.transpose(np.nonzero(toflash)):
            for nr, nc in neighbours(grid, r, c):
                if flashed[nr, nc]: continue
                inc[nr, nc] += 1
        flashed |= toflash
        grid += inc
        grid[flashed] = 0

    return np.all(flashed), np.sum(flashed), grid

def part1(fname: str):
    grid = read_array(fname)
    nrow, ncol = grid.shape
    
    total_flashes = 0
    for i in range(100):
        _, flashes, grid = step(grid)
        total_flashes += flashes
    print(f"part 1: {total_flashes}")

def part2(fname: str):
    grid = read_array(fname)
    nrow, ncol = grid.shape
    
    first = None
    for i in itertools.count(1):
        allflashed, _, grid = step(grid)
        if allflashed and first is None:
            first = i
            break
    print(f"part 2: {first}")

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])