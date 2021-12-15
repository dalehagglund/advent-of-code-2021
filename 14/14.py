import sys
import typing as ty
from dataclasses import dataclass, field
from enum import auto, Enum
import itertools
from itertools import tee, chain
from collections import Counter

def star(f):
    return lambda t: f(*t)

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

# add left and right sentinels to an iterator
def sentinels(items, left=None, right=None):
    return chain([left], items, [right])

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
            substitutions[tuple(left)] = right
        return frozenset(alphabet), template, substitutions

def step(poly: str, rules) -> str:
    result = []
    for c1, c2 in pairwise(poly):
        result.extend([c1, rules[ (c1, c2) ]])
    result.append(poly[-1])
    return "".join(result)
        
def part1(fname: str):
    alphabet, poly, rules = read_input(fname)
    for i in range(10):
        poly = step(poly, rules)

    first, *_, last = Counter(poly).most_common()
    print(f'part1: {first[1] - last[1]}')

def accumulate_sum(accum, counter, extra):
    accum.update(counter)
    accum[extra] -= 1
    return accum

def counts(cache, rules, depth, c1, c2):
    if depth == 0: return Counter(c1 + c2)
    ins = rules[(c1, c2)]
    return accumulate_sum(
        cache[ (c1, ins, depth-1) ].copy(),
        cache[ (ins, c2, depth-1) ],
        ins
    )

def print_cache(cache):
    items = sorted(cache.items(), key=star(lambda k, v: k[2:] + k[:2]))
    for k, v in items:
        print(
            f'   {k} -> ',
            " ".join(
                f'{count}{char}' for char, count in sorted(v.items())
            )
        )

def part2(fname: str):
    alphabet, poly, rules = read_input(fname)
    alphapairs = list(itertools.product(alphabet, repeat=2))

    cache = {}
    for depth in range(0, 41):
        for c1, c2 in alphapairs:
            cache[ (c1, c2, depth) ] = counts(cache, rules, depth, c1, c2)

    polypairs = [poly[i : i+2] for i in range(len(poly) - 1)]
    sum = cache[ (*polypairs[0], depth) ].copy()
    for left, right in pairwise(polypairs):
        accumulate_sum(sum, cache[ (*right, depth) ], right[0])

    first, *_, last = sum.most_common()
    print(f'part2: {first[1] - last[1]}')

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])