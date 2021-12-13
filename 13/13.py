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

def flip_at_row(mat, r):
    nr, nc = mat.shape
    print(f'flip row: {nr = } {nc = } {r = } ')

    upper = mat[0 : r, :]
    lower = mat[r+1 :, :]

    ur, _ = upper.shape
    lr, _ = lower.shape
    if lr != ur:
        lower = np.append(
            lower,
            np.zeros((ur - lr, nc), dtype=np.int32),
            axis=0)
    print_array(">>> flip row upper", upper)
    print_array(">>> flip row lower", lower)

    assert upper.shape == lower.shape, f'{upper.shape = } {lower.shape = }'

    newm = upper + np.flipud(lower)
    newm[newm > 0] = 1
    return newm

def flip_at_col(mat, c):
    nr, nc = mat.shape
    print(f'flip col: {nr = } {nc = } {c = }')

    left = mat[:, 0 : c]
    right = mat[:, c+1 :]

    _, lc = left.shape
    _, rc = right.shape
    if lc != rc:
        right = np.append(
            right,
            np.zeros((nr, lc - rc), dtype=np.int32),
            axis=1)
    print_array(">>> flip row left", left)
    print_array(">>> flip row right", right)

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
    print(f'{mat.shape = }')
    for i, (dim, n) in enumerate(folds):
        print(f'mat[{i}] {mat.shape = } {dim = } {n = }')
        print_array(f'> mat[{i}]', mat)
        mat = flips[dim](mat, n)
    print_array("final", mat)
    print("part 2:")

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])