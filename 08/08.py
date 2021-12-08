import typing as ty
import sys
from collections import defaultdict

segments = [
    "ABCEFG",
    "CF",
    "ACDEG",
    "ACDFG",
    "BCDF",
    "ABDFG",
    "ABDEFG",
    "ACF",
    "ABCDEFG",
    "ABCDFG",
]

display_value = {
    out: value
    for value, out
    in enumerate(segments)
}

def read_input(fname: str) -> ty.Iterator[ty.Tuple[ty.Set[str], ty.List[str]]]:
    with open(fname) as f:
        for line in f:
            left, right = line.strip().split(" | ")
            left = { "".join(sorted(s)) for s in left.split(" ") }
            right = [ sorted(s) for s in right.split(" ") ]
            yield (left, right)

def part1(fname):
    print("===== part 1")
    unique_lengths = {
        len(segments[i]) for i in [1, 4, 7, 8]
    }
    count = 0
    for left, right in read_input(fname):
        count += sum(len(s) in unique_lengths for s in right)
    print("part 1: ", count)

def solve(left: ty.Set[str], right: ty.List[str]):
    from functools import reduce
    solution = { wire: set("ABCDEFG") for wire in "abcdefg" }
    def with_len(n: int) -> ty.Set[str]:
        return { s for s in left if len(s) == n }

    def do_singleton(length: int, value: int):
        wires = with_len(length).pop()
        outputs = set(segments[value])
        for wire in wires:
            solution[wire] &= outputs
        for wire, sol in solution.items():
            if wire in wires:
                continue
            sol -= outputs

    def do_triple(length: int, values: ty.Set[int]):
        common_wires = set.intersection(*[set(w) for w in with_len(length)])
        common_outputs = set.intersection(*[set(segments[v]) for v in values])
        for wire in common_wires:
            solution[wire] &= common_outputs
        singletons = [ w for w, sol in solution.items() if len(sol) == 1 ]
        for wire, sol in solution.items():
            if len(sol) == 1:
                continue
            for w in singletons:
                sol -= solution[w]

    for nseg, value in [ (2, 1), (3, 7), (4, 4) ]:
        do_singleton(nseg, value)
    for nseg, values in [ (5, {2, 3, 5}), (6, {0, 6, 9}) ]:
        do_triple(nseg, values)

    for k in solution:
        solution[k] = solution[k].pop()

    def translate(wire: str) -> int:
        segs = "".join(sorted(solution[w] for w in wire))
        return str(display_value[segs])
    
    return int("".join(translate(wire) for wire in right))

def part2(fname):
    print("===== part 2")
    sum = 0
    for left, right in read_input(fname):
        sum += solve(left, right)
    print(sum)

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])