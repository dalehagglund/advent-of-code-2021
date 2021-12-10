from functools import reduce
import sys

class Illegal(Exception): pass
class Incomplete(Exception): pass

closes = {
    '(': ')',
    '[': ']',
    '<': '>',
    '{': '}',
}

trace = lambda *args: None
def bal(s, end, depth=0):
    trace(f'bal: {end = }')
    while True:
        i, c = next(s)
        trace(f"bal: {i = } {c = }")
        if c == '\n' and depth > 0:
            trace("#a")
            raise Incomplete("")
        elif c == '\n':
            trace("#b")
            return ""
        elif c == end:
            trace("#c")
            return end
        elif c in closes:
            trace("#d")
            try:
                bal(s, closes[c], depth+1)
            except Incomplete as exc:
                raise Incomplete(exc.args[0] + closes[c])
        else:
            trace("#e")
            raise Illegal(c)

def read_input(fname):
    with open(fname) as f:
        for line in f:
            yield line

test_input = [ 
    "()\n",
    "<>\n",
    "[]\n",
    "{}\n",
    "(())\n",
    "()<>\n",
    "([]{})\n",
    "(]\n",
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
        try:
            closing = bal(enumerate(iter(line)), "\n")
            assert closing == "", f"huh? {closing =}"
        except Illegal as exc:
            c = exc.args[0]
            syntax_score += syntax_scores[c]
        except Incomplete as exc:
            completion_scores.append(
                reduce(
                    lambda s, n: s * 5 + n,
                    (incomplete_scores[c] for c in exc.args[0]),
                    0
                )
            )
        
    print(f'part 1: {syntax_score}')

    completion_scores.sort()
    mid = len(completion_scores) // 2
    print(f'part 2: {completion_scores[mid]}')

if __name__ == '__main__':
    solve(sys.argv[1])