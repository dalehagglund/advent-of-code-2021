import numpy as np
from enum import Enum, auto
import typing as ty
import unittest

EMPTY = 0
SOUTH = 1
EAST = 2

def decode_lines(lines: ty.Iterable[str]) -> np.ndarray:
    translate: dict[str, int] = {
        '>': EAST,
        'v': SOUTH,
        '.': EMPTY,
    }
    return np.array([
        [translate[char] for char in line.strip()]
        for line in lines
    ], dtype=np.int8)

def read_input(fname: str) -> np.ndarray:
    with open(fname) as f:
        return decode_lines(f)

def can_move_east(grid) -> np.ndarray:
    mask = np.zeros_like(grid, dtype=np.bool8)
    mask[:, 0:-1] = (grid[:, 0:-1] == EAST) & (grid[:, 1:] == EMPTY)
    mask[:, -1]   = (grid[:,   -1] == EAST) & (grid[:, 0 ] == EMPTY)
    return mask

def can_move_south(grid) -> np.ndarray:
    mask = np.zeros_like(grid, dtype=np.bool8)
    mask[0:-1, :] = (grid[0:-1, :] == SOUTH) & (grid[1:, :] == EMPTY)
    mask[-1, :]   = (grid[-1, :] == SOUTH) & (grid[0, :] == EMPTY)
    return mask

def rotate_mask_east(mask) -> np.ndarray:
    new = np.zeros_like(mask)
    new[:, 1:] = mask[:, 0:-1]
    new[:, 0]  = mask[:, -1]
    return new

def rotate_mask_south(mask) -> np.ndarray:
    new = np.zeros_like(mask)
    new[1:, :] = mask[0:-1, :]
    new[0, :]  = mask[-1, :]
    return new

def move_east_herd(grid) -> bool:
    start = can_move_east(grid)
    if not np.any(start):
        return False
    end = rotate_mask_east(start)

    assert np.all(grid[start] == EAST)
    assert np.all(grid[end] == EMPTY)

    grid[start] = EMPTY
    grid[end] = EAST
    return True

def move_south_herd(grid) -> bool:
    start = can_move_south(grid)
    if not np.any(start):
        return False
    end = rotate_mask_south(start)

    assert np.all(grid[start] == SOUTH)
    assert np.all(grid[end] == EMPTY)

    grid[start] = EMPTY
    grid[end] = SOUTH
    return True

def print_grid(label, grid):
    letter = { EMPTY: ".", SOUTH: "v", EAST: ">"}
    print(label)
    nrows, ncols = grid.shape
    for i in range(nrows):
        print("    ", "".join(letter[v] for v in grid[i]))

def step(grid) -> bool:
    moved_east = move_east_herd(grid)
    moved_south = move_south_herd(grid)
    return moved_east or moved_south

def part1(fname: str):
    grid = read_input(fname)
    steps = 0
    print(grid)
    print_grid('initial grid', grid)
    while step(grid):
        steps += 1
        if steps % 20 == 0:
            print(f'... {steps} steps')
        # print_grid(f'after step {steps}', grid)
    print(f'part 1: steps until movement stops {steps+1}')

if __name__ == '__main__':
    import sys
    part1(sys.argv[1])
    sys.exit()

class MoveHerdEastTests(unittest.TestCase):
    def test_move_east(self):
        tests = [
            [ [ "...", ".>.", "..." ], True,  [ "...", "..>", "..." ] ],
            [ [ "...", ".>>", "..." ], True,  [ "...", ">>.", "..." ] ],
            [ [ "...", ">>>", "..." ], False, [ "...", ">>>", "..." ] ]
        ]

        for i, (input, moved, expected) in enumerate(tests):
            with self.subTest(f'subtest {i}'):
                grid = decode_lines(input)
                expected = decode_lines(expected)
                result = move_east_herd(grid)
                self.assertEqual(moved, result)
                self.assertTrue(np.all(grid == expected))

class DecodeTests(unittest.TestCase):
    def one_input_line(self):
        lines = [ "v>.\n" ]
        grid = decode_lines(lines)
        self.assertEqual((1, 3), grid.shape)
        self.assertEqual((SOUTH, EAST, EMPTY) == tuple(grid[0]))

class RotateRightDownMasks(unittest.TestCase):
    def test_rotate_right_mask(self):
        tests = [
            [ [0, 0, 0], [0, 0, 0] ],
            [ [1, 0, 0], [0, 1, 0] ],
            [ [0, 1, 0], [0, 0, 1] ],
            [ [0, 0, 1], [1, 0, 0] ],
            [ [1, 1, 0], [0, 1, 1] ],
            [ [0, 1, 1], [1, 0, 1] ],
            [ [1, 0, 1], [1, 1, 0] ],
            [ [1, 1, 1], [1, 1, 1] ],
        ]
        for i, (input, expected) in enumerate(tests):
            with self.subTest(f'subtest {i}: input |{input}|'):
                mask = np.array([input], dtype=np.bool8)
                rotated = rotate_mask_east(mask)
                self.assertEqual(expected, list(rotated[0]))
    def test_rotate_down_mask(self):
        tests = [
            [ [0, 0, 0], [0, 0, 0] ],
            [ [1, 0, 0], [0, 1, 0] ],
            [ [0, 1, 0], [0, 0, 1] ],
            [ [0, 0, 1], [1, 0, 0] ],
            [ [1, 1, 0], [0, 1, 1] ],
            [ [0, 1, 1], [1, 0, 1] ],
            [ [1, 0, 1], [1, 1, 0] ],
            [ [1, 1, 1], [1, 1, 1] ],
        ]
        for i, (input, expected) in enumerate(tests):
            with self.subTest(f'subtest {i}: input |{input}|'):
                mask = np.array([input], dtype=np.bool8).transpose()
                rotated = rotate_mask_south(mask)
                self.assertEqual(expected, list(rotated[:, 0]))

class MoveRightDownMasks(unittest.TestCase):
    def test_move_right_mask(self):
        tests = [ 
            ( "...", (0, 0, 0) ),
            ( ">..", (1, 0, 0) ),
            ( ".>.", (0, 1, 0) ),
            ( "..>", (0, 0, 1) ),
            ( ">>.", (0, 1, 0) ),
            ( ".>>", (0, 0, 1) ),
            ( ">>>", (0, 0, 0) ),
        ]
        for i, (line, expected) in enumerate(tests):
            with self.subTest(f'subtest {i}: line |{line}|'):
                grid = decode_lines([line])
                mask = can_move_east(grid)
                self.assertEqual(expected, tuple(mask[0]))
    def test_move_down_mask(self):
        tests = [
            # each string represents a column. this
            # is dealt by transposing the result of
            # decode_lines
            ("...", (0, 0, 0) ),
            ( "v..", (1, 0, 0) ),
            ( ".v.", (0, 1, 0) ),
            ( "..v", (0, 0, 1) ),
            ( "vv.", (0, 1, 0) ),
            ( ".vv", (0, 0, 1) ),
            ( "vvv", (0, 0, 0) ),
        ]
        for i, (col, expected) in enumerate(tests):
            with self.subTest(f'subtest {i}: col |{col}|'):
                grid = decode_lines([col]).transpose() 
                mask = can_move_south(grid)
                self.assertEqual(expected, tuple(mask[:, 0]))