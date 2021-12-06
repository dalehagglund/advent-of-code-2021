import sys
import typing as ty
from collections import defaultdict

RESET_VALUE = 6
NEWFISH_PENALTY = 2

def step(fish: ty.List[int]):
    newfish: int = 0
    for i, days in enumerate(fish):
        if days == 0:
            newfish += 1
            fish[i] = RESET_VALUE
        else:
            fish[i] -= 1
    fish.extend(
        RESET_VALUE + NEWFISH_PENALTY
        for _ in range(newfish))

def read_fish(line):
    return list(map(int, line.strip().split(",")))

def part1(file):
    print("===== PART 1")
    with open(file) as f:
        fish = read_fish(f.readline())
    for _ in range(80):
        step(fish)
    print(len(fish))

def recurrence_step(t: ty.Tuple[int]) -> ty.Tuple[int]:
    f0, f1, f2, f3, f4, f5, f6, f7, f8 = t
    return (
        f1,
        f2,
        f3, 
        f4,
        f5,
        f6,
        f7 + f0,
        f8,
        f0)

def part2(file):
    print("===== PART 2")
    with open(file) as f:
        fish = read_fish(f.readline())
    counts = defaultdict(lambda: 0)
    for days in fish:
        counts[days] += 1
    state = tuple(counts[i] for i in range(9))
    for _ in range(256):
        state = recurrence_step(state)
    print(sum(state))


if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])