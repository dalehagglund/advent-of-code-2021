import itertools
import typing as ty
from enum import Enum, auto
from dataclasses import dataclass, field
import numpy as np
import sys
import heapq as hq
from itertools import count
import time
import math

def read_input(fname: str):
    with open(fname) as f:
        return np.array([
            list(map(int, line.strip()))
            for line in f
        ], dtype=np.int32)

Coord = ty.Tuple[int, int]

def neighbours(grid, row, col) -> ty.Iterable[ty.Tuple[int, int]]:
    nrow, ncol = grid.shape
    if 0 < row: yield (row - 1, col)
    if row < nrow - 1: yield (row + 1, col)
    if 0 < col: yield (row, col - 1)
    if col < ncol - 1: yield (row, col + 1)

class StopWatch:
    def __init__(self, timesource=None):
        self._now: ty.Callable[[], float] = timesource or time.perf_counter
        self._start: float = self._now()
        self._prevlap: float = self._start
    def elapsed(self) -> float:
        return self._now() - self._start
    def lap(self) -> float:
        now = self._now()
        laptime = now - self._prevlap
        self._prevlap = now
        return laptime

#
# This is translated directly from the description of Dijkstra's
# algorithm for finding a least cost spanning tree rooted at a given
# node, as given in _The Algorithm Design Manual_, 3rd ed, by Steven
# Skiena
#

def dijkstra(costs, start, end):
    nrow, ncol = costs.shape
    print(f'dijkstra: {costs.shape = } {start = }')
    maxint = np.iinfo(np.int32).max

    weight = 0
    intree = np.full_like(costs, fill_value=0, dtype=np.bool8)
    distance = np.full_like(costs, fill_value=maxint)
    parent = np.full_like(costs, fill_value=None, dtype=np.dtype('object'))

    timer = StopWatch()
    dist = None
    distance[start] = 0
    v = start

    def dist_to(p, q):
        x0, y0 = p
        x1, y1 = q
        return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

    def progress(tag, iters, coord):
        print(" ".join([
            f'... {timer.lap():.3f} iters {iters:>6}',
            f'coord {coord}',
            f'pathc {distance[coord]}',
            f'dstart {dist_to(start, coord):.1f}',
            f'dend {dist_to(end, coord):.1f}',
        ]))

    every = 2500
    loops = 0

    while not intree[v]:
        loops += 1
        if loops % every == 0:
            progress('' if v != end else 'end!', loops, v)

        intree[v] = True
        if v != start:
            # because this loop is only entered on the 
            # second and subsequent iterations, the 
            # values `dist` and `parent[v]` have already
            # been computed by the previous iteration
            # and so it only *looks* like we
            # might be accessing undefined variables

            # print(f'adding edge {parent[v]} -> {v} to mst')
            weight += dist   

        coords = neighbours(costs, *v)
        for coord in coords:
            if distance[coord] > distance[v] + costs[coord]:
                distance[coord] = distance[v] + costs[coord]
                parent[coord] = v

        o = np.argmin(np.where(~intree, distance, maxint), axis=None)
        v = np.unravel_index(o, distance.shape)
        dist = distance[v]

        # there has to be a much better numpy way of doing this
        # (using masked arrays?), but the following is a direct
        # translation from Skiena.
        # dist = maxint
        # for coord in itertools.product(range(nrow), range(ncol)):
        #     if not intree[coord] and dist > distance[coord]:
        #         dist = distance[coord]
        #         v = coord

    # after the loop, we now have a shortest-path spanning tree
    # rooted at the start node. return that and the parent data
    # for reconstructing the shortest paths.

    return parent, distance
    
def find_safest(costs, start, end):
    parent, dist = dijkstra(costs, start, end)
    return dist[end]

def part1(fname: str):
    print("=" * 10, "part 1")
    grid = read_input(fname)
    nrow, ncol = grid.shape

    best = find_safest(grid, (0, 0), (nrow - 1, ncol - 1))
    print(f'part1: {best}')

def expand_grid(grid, factor):
    nrow, ncol = grid.shape
    newgrid = np.zeros_like(grid, shape=(nrow * factor, ncol * factor))
    # print(f'input shape: {grid.shape}')
    # print(f'desired shape: {newgrid.shape}')

    # print(f'input block: ')
    # print(grid)

    for b in range(factor):
        for c in range(factor):
            block = grid.copy()
            for _ in range(b + c):
                block += 1
                block[block > 9] = 1
            # print(f'block {b}, {c}: ')
            # print(block)
            assert not np.any(block < 0) and not np.any(block > 9)
            newgrid[
                b * nrow : (b + 1) * nrow,
                c * ncol : (c + 1) * ncol
            ] = block
    
    return newgrid

def part2(fname: str):
    print("=" * 10, "part 2")

    grid = read_input(fname)
    expanded = expand_grid(grid, 5)
    # print(expanded)
    nrow, ncol = expanded.shape

    best = find_safest(expanded, (0, 0), (nrow - 1, ncol - 1))
    print(f'part2: {best}')

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])