from enum import Enum, auto
import sys
from functools import reduce

class Status(Enum):
    OK = auto()
    MISMATCH = auto()
    INCOMPLETE = auto()

def bal(s: str):
    pending = []
    match = dict("[] () <> {}".split())
    opening = frozenset(match.keys())
    closing = frozenset(match.values())

    for c in s:
        if c == "\n" and not pending:
            return Status.OK, None
        elif c == "\n" and pending:
            return Status.INCOMPLETE, "".join(reversed(pending))
        elif c in opening:
            pending.append(match[c])
        elif c in closing and c == pending[-1]:
            pending.pop()
        elif c in closing and c != pending[-1]:
            return Status.MISMATCH, c

    assert False, "huh? shouldn't have fallen off the string"

def read_input(fname):
    with open(fname) as f:
        yield from f

test_input = [ 
    "()\n",
    "<>\n",
    "[]\n",
    "{}\n",
    "(())\n",
    "()<>\n",
    "([]{})\n",
    "(]\n",
    "(<{\n",
]

syntax_scores = {
    ')': 3,
    ']': 57,
    '}': 1197,
    '>': 25137,
}

incomplete_scores = {
    ')': 1,
    ']': 2,
    '}': 3,
    '>': 4,
}

def solve(fname):
    lines = read_input(fname)
    syntax_score = 0
    completion_scores = []

    for line in lines:
        # print(f"---> {line.strip()}")
        status, result = bal(line)
        # print(status, result)

        if status == Status.OK:
            pass
        elif status == Status.MISMATCH:
            syntax_score += syntax_scores[result]
        elif status == Status.INCOMPLETE:
            completion_scores.append(
                reduce(
                    lambda s, n: s * 5 + n,
                    (incomplete_scores[c] for c in result),
                    0
                )
            )
        
    print(f'part 1: {syntax_score}')

    completion_scores.sort()
    mid = len(completion_scores) // 2
    print(f'part 2: {completion_scores[mid]}')

if __name__ == '__main__':
    solve(sys.argv[1])