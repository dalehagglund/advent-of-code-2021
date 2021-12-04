"""
Advent of Code 2021
Day 3: Binary Diagnostic

https://adventofcode.com/2021/day/3
"""

from itertools import starmap
import operator as op
from functools import reduce, partial
import sys

def read_diagnostics():
    with open(sys.argv[1]) as f:
        line: str
        for line in f:
            yield tuple(map(int, line.strip()))

def sum_bits(w1, w2):
    return tuple(starmap(op.add, zip(w1, w2)))

def frombin(word):
    return int(
        "".join(str(b) for b in word),
        base=2
    )

def part1():
    words = list(read_diagnostics())
    nwords = len(words)
    bitsums = reduce(sum_bits, words)

    gword = tuple(map(lambda s: int(s > nwords/2), bitsums))
    eword = tuple(map(lambda s: int(s < nwords/2), bitsums))

    gamma = frombin(gword)
    epsilon = frombin(eword)
    print(gamma * epsilon)

def oxy_selbit(t):
    if   t[0] > t[1]: return 0
    elif t[0] < t[1]: return 1
    else:             return 1

def co2_selbit(t):
    if   t[0] < t[1]: return 0
    elif t[0] > t[1]: return 1
    else:             return 0

def zero_one_sums(words):
    z = reduce(sum_bits, words)
    z = list(map(lambda s: (len(words) - s, s), z))
    return z

def part2():
    orig_words = list(read_diagnostics())

    def filter_words(words, selbit):
        words = words[:]
        for i in range(len(words[0])):
            sums = zero_one_sums(words)
            bit = selbit(sums[i])
            # print(i, sums[i], selbit, print(len(words)))
            words = list(filter(lambda w: w[i] == bit, words))
            if len(words) == 1:
                break
        assert len(words) == 1, "huh?"
        return words[0]

    oxy_word = filter_words(orig_words, oxy_selbit)
    co2_word = filter_words(orig_words, co2_selbit)

    oxy = frombin(oxy_word)
    co2 = frombin(co2_word)

    print(oxy * co2)

if __name__ == "__main__":
    print("==== PART ONE ====")
    part1()
    print("==== PART TWO ====")
    part2()