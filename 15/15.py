import itertools
import typing as ty
from enum import Enum, auto
from dataclasses import dataclass, field
import numpy as np
import sys
import heapq as hq
from itertools import count
import time

def read_input(fname: str):
    with open(fname) as f:
        return np.array([
            list(map(int, line.strip()))
            for line in f
        ])

Coord = ty.Tuple[int, int]

@dataclass
class NodeState:
    loc: Coord
    cost_so_far: int = 0
    est_remaining: int = float('+inf')
    prev: ty.Optional[Coord] = None

    def cost_estimate(self):
        return self.cost_so_far + self.est_remaining
    
class PrioQueue:
    def __init__(self):
        self._counter = count()
        self._heap = []
        self._coords = set()
        self._resorts = 0
        hq.heapify(self._heap)
    def pop(self):
        _, _, item = hq.heappop(self._heap)
        self._coords.remove(item.loc)
        return item
    def insert(self, item: NodeState):
        self._coords.add(item.loc)
        hq.heappush(
            self._heap,
            (item.cost_estimate(), next(self._counter), item))
    def update_order(self):
        self._resorts += 1
        self._heap = [
            (item.cost_estimate(), c, item)
            for _, c, item
            in self._heap
        ]
        hq.heapify(self._heap)
    def empty(self):
        return len(self._heap) == 0
    def contains(self, coord):
       return coord in self._coords
    def resorts(self):
        return self._resorts

def neighbours(grid, row, col) -> ty.Iterable[ty.Tuple[int, int]]:
    nrow, ncol = grid.shape
    if 0 < row: yield (row - 1, col)
    if row < nrow - 1: yield (row + 1, col)
    if 0 < col: yield (row, col - 1)
    if col < ncol - 1: yield (row, col + 1)

def find_safest(costs, start, end):
    nrow, ncol = costs.shape
    print(f'{costs.shape = } {start = } {end = }')

    nodes = np.empty(costs.shape, dtype=np.dtype('object'))
    open = PrioQueue()
    closed: ty.Set[Coord] = set()

    def dist(c):
        crow, ccol = c
        erow, ecol = end
        return abs(crow - erow)  + abs(ccol - ecol)

    nodes[start] = NodeState(
        loc = start,
        cost_so_far = 0,
        est_remaining = dist(start), 
        prev = None
    )

    open.insert(nodes[start])
 
    # trace = print
    trace = lambda *_: None

    itercount = 0
    report_every = 500
    t = time.perf_counter()

    while not open.empty():
        # if maxiter == 0: break
        # maxiter -= 1
        itercount += 1
        # trace(f'open:   ', [ (n.loc, n.cost_estimate()) for _, _, n in open._heap ])
        # trace(f'closed: ', sorted(closed))

        cur = open.pop()
        trace(f">>> pop {cur}")
        if itercount % report_every == 0:
            now = time.perf_counter()
            print(
                f'dt {now - t:.3f} iter {itercount} open {len(open._heap)}',
                f'closed {len(closed)} resorts {open.resorts()} {cur}',
            )
            t = now

        closed |= { cur.loc }
        if cur.loc == end:
            trace(f">>> found the end: {cur.cost_so_far}")
            return cur.cost_so_far

        for nc in neighbours(costs, *cur.loc):
            trace(f">>> considering neighbour {nc}")
            if nc in closed: 
                trace(f">>> ... closed")
            elif not open.contains(nc):
                trace(f">>> ... not found in open")
                nodes[nc] = NodeState(
                    loc = nc,
                    cost_so_far = cur.cost_so_far + costs[nc],
                    est_remaining = dist(nc), 
                    prev = cur.loc,
                )
                trace(f">>> ... inserting {nodes[nc]}")
                open.insert(nodes[nc])
            else:
                found = nodes[nc]
                trace(f">>> ... found in open {found}")
                trace(f">>> ... {cur.cost_so_far = } {costs[nc] = }")
                if cur.cost_so_far + costs[nc] < found.cost_so_far:
                    trace(f'>>> ... updating cost and prev')
                    found.prev = cur.loc
                    found.cost_so_far = cur.cost_so_far + costs[nc]
                    trace(f">>> ... updated found {found}")
                    open.update_order()
                else:
                    trace(f">>> ... unchanged")
        trace()

    assert False, "huh? paths exhausted?"

def part1(fname: str):
    print("=" * 10, "part 1")
    grid = read_input(fname)
    nrow, ncol = grid.shape

    print(grid.shape)
    print(grid)

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

    # grid2 = read_input("tiny_expanded.txt")
    # print(expanded.shape)
    # eq = np.equal(grid2, expanded)
    # maxout = 50
    # for pos in itertools.product(range(nrow), range(ncol)):
    #     if not eq[pos]:
    #         print(f'{pos = } {expanded[pos] = } {grid2[pos] = }')
    #         maxout -= 1
    #         if maxout == 0: break
    
    best = find_safest(expanded, (0, 0), (nrow - 1, ncol - 1))
    # best = find_safest(expanded, (0, 0), (99, 99))
    print(f'part2: {best}')

if __name__ == '__main__':
    # part1(sys.argv[1])
    part2(sys.argv[1])