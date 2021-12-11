#
# a solution reasoning from the observations,
# with no direct calculation of the permutation of segments
#

import typing as ty
from enum import Enum, auto

class Seg(Enum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()
    G = auto()

Observation = ty.FrozenSet[Seg]

def to_observation(s: str) -> Observation:
    return frozenset(Seg[c] for c in s.upper())

def to_str(o: Observation) -> str:
    return "".join(sorted(seg.name for seg in o))

def read_input(
    fname: str
) -> ty.Tuple[ty.FrozenSet[Observation], ty.List[Observation]]:
    with open(fname) as f:
        for line in f:
            left, right = line.strip().split(" | ")
            observations = frozenset(
                to_observation(s)
                for s
                in left.split(" ") 
            )
            panel = [
                to_observation(s)
                for s 
                in right.split(" ")
            ]
            yield (observations, panel)

def unique(
    s: ty.FrozenSet[Observation], predicate
) -> Observation:
    candidates = find(s, predicate)
    assert len(candidates) == 1, \
        'unique: {}'.format(" ".join(map(to_str, candidates)))
    return next(iter(candidates))

def find(
    s: ty.FrozenSet[Observation],
    predicate
) -> ty.FrozenSet[Observation]:
    return frozenset(filter(predicate, s))

def solve(
    observations: ty.FrozenSet[Observation],
    panel: ty.List[Observation]
) -> int:
    ## initialize mapping with observations that can be
    ## uniquely determined based just on the number of
    ## segments lit up

    obs: ty.Dict[int, Observation] = {
        1: unique(observations, lambda o: len(o) == 2),
        4: unique(observations, lambda o: len(o) == 4),
        7: unique(observations, lambda o: len(o) == 3),
        8: unique(observations, lambda o: len(o) == 7),
    }

    ## now consider of length 5, which must be the digits 2, 3, 5.

    choice235 = find(observations, lambda o: len(o) == 5)
    assert(len(choice235) == 3)

    # in the standard encoding, the segments of 3 are superset of 1
    # and 7, so find the unique candidate for which that's true

    obs[3] = unique(
        choice235,
        lambda o: o > obs[1] and o > obs[7]
    )
    choice25 = choice235 - { obs[3] }

    # next, we distinguish between 2 and 5 by noting that
    #
    # 1. | enc(2) \intersect enc(4) | == 2
    # 2. | enc(5) \intersect enc(4) | == 3
    #
    # where enc(n) represents the standard encoding of n

    obs[2] = unique(choice25, lambda o: len(o & obs[4]) == 2)
    obs[5] = unique(choice25, lambda o: len(o & obs[4]) == 3)
    assert { obs[2], obs[5] } == choice25

    ## now consider the observations of length 6, which must
    ## be the digits 0, 6, 9

    choice069 = find(observations, lambda o: len(o) == 6)
    assert len(choice069) == 3

    # first observe that 6 and 9 are supersets of 5 but 0
    # is not a superset of 5.

    obs[0] = unique(choice069, lambda o: not(o > obs[5]))
    choice69 = choice069 - { obs[0] }

    # next note that
    #
    # 1. enc(9) \superset enc(3), and
    # 2. enc(6) \not \superset enc(3)

    obs[9] = unique(choice69, lambda o: o > obs[3])
    obs[6] = unique(choice69, lambda o: not (o > obs[3]))

    assert { obs[9], obs[6] } == choice69

    ## now compute the reverse mapping from observations to digit
    ## and compute the value displayed on the panel

    digit = { o: str(d) for d, o in obs.items() }
    
    return int("".join(digit[o] for o in panel))

def part2(fname: str):
    panel_total = sum(
        solve(observations, panel)
        for observations, panel
        in read_input(fname)
    )
    print(f'part 2: {panel_total}')

if __name__ == '__main__':
    import sys
    part2(sys.argv[1])