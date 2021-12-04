"""
Advent of Code 2021, Day 1: Sonar Sweep

https://adventofcode.com/2021/day/1
"""

import typing as ty
from itertools import tee, starmap

def star(f): return lambda t: f(*t)

def pairwise(iterable: ty.Iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def advance(iter, count):
    for _ in range(count):
        next(iter, None)

def sliding_window(iterable: ty.Iterable, n: int = 2):
    iters = list(tee(iterable, n))
    for count, iter in enumerate(iters):
        advance(iter, count)
    return zip(*iters)

def read_measurements():
    with open("input.txt") as f:
        yield from map(int, f)

def count_increases(winsize=1):
    def increasing(a, b) -> bool: return b > a

    s = read_measurements()
    if winsize > 1:
        s = sliding_window(s, winsize)
        s = map(sum, s)
    s = sliding_window(s, 2)
    s = map(star(increasing), s)

    return sum(s)