import typing as ty
import sys
from collections import defaultdict

output = [
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
    in enumerate(output)
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
        len(output[i]) for i in [1, 4, 7, 8]
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

    # print(f'{sorted(left) = }')
        
    def do_singleton(length: int, value: int):
        word = with_len(length).pop()
        for wire in word:
            solution[wire] &= set(output[value])
        for wire, sol in solution.items():
            if wire in word:
                continue
            sol -= set(output[value])

    def do_triple(length: int, values: ty.Set[int]):
        words = with_len(length)
        common_words = reduce(set.intersection, [ set(w) for w in words ])
        common_outputs = reduce(set.intersection, [ set(output[v]) for v in values ])
        for wire in common_words:
            solution[wire].intersection_update(common_outputs)
        singletons = [ w for w, sol in solution.items() if len(sol) == 1 ]
        for wire, sol in solution.items():
            if len(sol) == 1:
                continue
            for w in singletons:
                sol -= solution[w]
            # sol.difference_update(solution[w] for w in singletons)

    do_singleton(2, 1)
    do_singleton(3, 7)
    do_singleton(4, 4)

    do_triple(5, {2, 3, 5})
    do_triple(6, {0, 6, 9})

    for k in solution:
        solution[k] = solution[k].pop()
    # print(f'{solution = }')

    def translate(wire: str) -> int:
        out = "".join(
            sorted(solution[w] for w in wire)
        )
        return str(display_value[out])
    
    panel = int("".join(
       translate(wire) for wire in right 
    ))
    return panel

def part2(fname):
    print("===== part 2")
    sum = 0
    for left, right in read_input(fname):
        sum += solve(left, right)
    print(sum)

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])