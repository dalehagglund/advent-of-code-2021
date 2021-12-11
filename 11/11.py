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

def bool_like(a):
    return np.zeros_like(a, dtype=np.bool8)

def step(grid):
    def neighbours(a, i, j):
        return (
            slice(max(0, i - 1), i + 2),
            slice(max(0, j - 1), j + 2)
        )

    flashed = bool_like(grid)
    grid += 1
    while np.any(grid > 9):
        inc = np.zeros_like(grid)
        toflash = grid > 9
        # this increments the flashed cells as well, but we
        # reset all the flashed cells to zero anyway at the
        # end of the loop
        for r, c in np.argwhere(toflash):
            inc[neighbours(grid, r, c)] += 1
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