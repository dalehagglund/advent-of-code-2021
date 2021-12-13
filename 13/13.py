import sys
import typing as ty
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np

def print_array(label, m):
    print(f">>> arrray {label} {m.shape = } {np.sum(m) = }<<<")
    nrow, ncol = m.shape
    for r in range(nrow):
        print("".join(".#"[m[r, c]] for c in range(ncol)))


def read_input(fname: str):
    labels = { 'x': 'col', 'y': 'row' }
    with open(fname) as f:
        coords = []
        folds = []
        while (line := next(f)) != '\n':
            c, r = map(int, line.strip().split(","))
            coords.append((r, c))
        for line in f:
            _, _, instr = line.strip().split()
            dim, n = instr.split("=")
            folds.append((labels[dim], int(n)))

    maxrow = max(coords, key=lambda t: t[0])[0] + 1
    maxcol = max(coords, key=lambda t: t[1])[1] + 1
    m = np.zeros((maxrow, maxcol), dtype=np.int32)
    for r, c in coords:
        m[r, c] = 1
    return folds, m

def zero_extend(desired, mat):
    assert sum(x != y for x, y in zip(desired, mat.shape)) < 2, \
        f'shapes must match in 0 or 1 places: {desired} {mat.shape}'

    if desired == mat.shape:
        return mat

    desired_rows, desired_cols = desired
    mat_rows, mat_cols = mat.shape

    if desired_rows != mat_rows:
        assert mat_rows < desired_rows
        zrows = desired_rows - mat_rows
        zcols = desired_cols
        axis = 0
    elif desired_cols != mat_cols:
        assert mat_cols < desired_cols
        zrows = desired_rows
        zcols = desired_cols - mat_cols
        axis = 1
    else:
        assert "huh?"


    return np.append(
        mat, 
        np.zeros((zrows, zcols), dtype=np.int32),
        axis=axis)

def flip_at_row(mat, r):
    nr, nc = mat.shape
    print(f'flip row: {nr = } {nc = } {r = } ')

    upper = mat[0 : r, :]
    lower = mat[r+1 :, :]

    lower = zero_extend(upper.shape, lower)
    assert upper.shape == lower.shape, f'{upper.shape = } {lower.shape = }'

    newm = upper + np.flipud(lower)
    newm[newm > 0] = 1
    return newm

def flip_at_col(mat, c):
    nr, nc = mat.shape
    print(f'flip col: {nr = } {nc = } {c = }')

    left = mat[:, 0 : c]
    right = mat[:, c+1 :]

    right = zero_extend(left.shape, right)
    assert left.shape == right.shape, f'{left.shape = } {right.shape = }'

    newm = left + np.fliplr(right)
    newm[newm > 0] = 1
    return newm

flips = {
    "row": flip_at_row,
    "col": flip_at_col,
}

def part1(fname: str):
    print("===== PART 1 =====")
    folds, m = read_input(fname)
    dim, n = folds[0]
    # print(f'flip: {dim=} {n=}')
    newm = flips[dim](m, n)
    print(f'part1: {np.sum(newm)}')

def part2(fname: str):
    print("===== PART 2 =====")
    folds, mat = read_input(fname)
    # print(f'{mat.shape = }')
    for i, (dim, n) in enumerate(folds):
        # print(f'mat[{i}] {mat.shape = } {dim = } {n = }')
        # print_array(f'> mat[{i}]', mat)
        mat = flips[dim](mat, n)
    print_array("final", mat)
    print("part 2:")

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])