import numpy as np
import typing as ty
import itertools

def read_input(fname: str):
    def to_bit(c: str) -> int:
        assert c in "#."
        return 1 if c == "#" else 0
    def to_algo(s: str) -> np.ndarray:
        return (
            np
            .array([to_bit(c) for c in s], dtype=np.int8)
            .reshape(2, 2, 2, 2, 2, 2, 2, 2, 2)
        )

    with open(fname) as f:
        algo = to_algo(next(f).strip())
        next(f)
        image = np.array([
            [ to_bit(c) for c in line.strip() ]
            for line in f
        ], dtype=np.int8)

    return algo, image

def neighbour_tuple(grid, i, j, fill=None):
    nrow, ncol = grid.shape
    def cell(i, j):
        if 0 <= i < nrow and 0 <= j < ncol:
            return grid[i, j]
        else:
            return fill
    return tuple(
        cell(i + di, j + dj)
        for di, dj
        in itertools.product((-1, 0, +1), repeat=2)
    )

def print_grid(tag: str, g: np.ndarray):
    print(tag)
    nrow, ncol = g.shape
    for i in range(nrow):
        print(
            "    ",
            "".join(".#"[g[i, j]] for j in range(ncol)),
        )

class InfGrid:
    def __init__(self, algo, image):
        self._algo = algo
        self._image = image
        self._fill_value = 0

    def lit_count(self):
        assert self._fill_value == 0, "count is infinite!"
        return np.sum(self._image)

    def fill(self): return self._fill_value

    def enhance(self):
        self._expand()
        next = np.zeros_like(self._image)
        nrow, ncol = self._image.shape
        for i, j in itertools.product(range(nrow), range(ncol)):
            next[i, j] = self._algo[
                neighbour_tuple(self._image, i, j, fill=self._fill_value)
            ]
        self._fill_value = self._algo[ (self._fill_value,) * 9]
        self._image = next

    def _expand(self):
        nrow, ncol = self._image.shape
        g = np.full_like(
            self._image,
            shape=(nrow+2, ncol+2),
            fill_value=self._fill_value)
        g[1: 1+nrow, 1: 1+ncol] = self._image
        self._image = g

def part1(fname: str):
    algo, image = read_input(fname)

    inf = InfGrid(algo, image)

    print_grid(f"gen 0 (fill: {inf.fill()})", inf._image)
    inf.enhance()
    print_grid(f"gen 1 (fill: {inf.fill()})", inf._image)
    inf.enhance()
    print_grid(f"gen 2 (fill: {inf.fill()})", inf._image)

    print(f'part 1: total lit {inf.lit_count()}')

if __name__ == '__main__':
    import sys
    part1(sys.argv[1])
    sys.exit(0)

import unittest

class NeighbourTests(unittest.TestCase):
    def test_1(self):
        g = np.arange(9).reshape(3, 3)
        self.assertEqual(tuple(range(9)), neighbour_tuple(g, 1, 1))
    def test_2(self):
        g = np.arange(9).reshape(3, 3)
        self.assertEqual(
            (None, None, None, None, 0, 1, None, 3, 4),
            neighbour_tuple(g, 0, 0))
