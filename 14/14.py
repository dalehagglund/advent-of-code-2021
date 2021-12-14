import itertools

import sys
import typing as ty
from dataclasses import dataclass, field
from enum import auto, Enum
from itertools import tee, chain
from collections import Counter

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def read_input(fname:str):
    with open(fname) as f:
        alphabet = set()
        substitutions = {}
        template = next(f).strip()
        next(f)
        for line in f:
            left, right = line.strip().split(" -> ")
            alphabet.update(left)
            alphabet.update(right)
            substitutions[left] = right
            substitutions[tuple(left)] = right
        return frozenset(alphabet), template, substitutions

def step(poly: str, rules) -> str:
    result = []
    for c1, c2 in pairwise(poly):
        ins = rules.get(c1 + c2, '')
        assert ins != ''
        result.extend([c1, rules.get(c1 + c2, '')])
    result.append(poly[-1])
    return "".join(result)
        
def part1(fname: str):
    alphabet, poly, rules = read_input(fname)
    for i in range(10):
        poly = step(poly, rules)

    counts = Counter(poly)
    seq = counts.most_common()
    first, *_, last = seq
    print(f'part1: {first[1] - last[1]}')

def counts(cache, rules, depth, c1, c2):
    if depth == 0:
        return Counter(c1 + c2)

    ins = rules[(c1, c2)]

    c = Counter()
    c.update(cache[ (c1, ins, depth-1) ] )
    c.update(cache[ (ins, c2, depth-1) ] )
    c[ins] -= 1

    return c

def star(f):
    return lambda t: f(*t)

def print_cache(cache):
    items = sorted(cache.items(), key=star(lambda k, v: k[2:] + k[:2]))
    for k, v in items:
        print(
            f'   {k} -> ',
            " ".join(
                f'{count}{char}'
                for char, count
                in sorted(v.items())
            )
        )

def part2(fname: str):
    alphabet, poly, rules = read_input(fname)
    depth = 40

    cache = {}
    alphapairs = list(itertools.product(alphabet, repeat=2))
    for depth in range(0, depth + 1):
        for c1, c2 in alphapairs:
            cache[ (c1, c2, depth) ] = counts(cache, rules, depth, c1, c2)

    pairs = pairwise(chain(
        [None], 
        ("".join(p) for p in pairwise(poly)),
        [None],
    ))

    c: Counter = Counter()
    for left, right in pairs:
        if left is None:
            c.update(cache[ (*right, depth) ])
        elif right is None:
            pass
        else:
            c.update(cache[ (*right, depth) ])
            c[right[0]] -= 1

    seq = c.most_common()
    first, *_, last = seq
    print(f'part1: {first[1] - last[1]}')

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])