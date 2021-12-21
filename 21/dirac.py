import sys
import random
from collections import Counter
from itertools import islice, product
from functools import lru_cache, reduce
import operator

def det100():
    roll = 1
    while True:
        yield roll
        roll += 1
        if roll > 100:
            roll = 1

def roll3(die):
    a, b, c = next(die), next(die), next(die)
    return a + b + c

def step(die, pos) -> int:
    move = roll3(die)
    return ((pos - 1) + move) % 10 + 1

def game(die, start1, start2) -> int:
    nextplayer = [1, 0]
    curplayer = 0

    position = [ start1, start2 ]
    score = [ 0, 0 ]
    turns = 0

    while max(score) < 1000:
        turns += 1
        nextpos = step(die, position[curplayer])
        score[curplayer] += nextpos
        position[curplayer] = nextpos
        print(f'player {curplayer+1}: pos {position[curplayer]} score {score[curplayer]}')
        curplayer = nextplayer[curplayer]

    print(f'final: {score}')
    return (3 * turns) * min(score)

def part1(fname: str):
    print(f'{step(iter([2, 2, 1]), 7)}')
    result = game(det100(), 9, 3)
    print(f'part 1: {result}')

qmult = {
    3: 1,
    4: 3,
    5: 6,
    6: 7,
    7: 6,
    8: 3,
    9: 1,
}
# qmult = Counter(map(sum, product(range(1, 4), repeat=3)))
qrolls = frozenset(qmult.keys())

IntPair = tuple[int, int]

def mul(terms):
    return reduce(operator.mul, terms, 1)

def replace_index(t: tuple, i: int, newval: int) -> IntPair:
    assert 0 <= i < len(t), ("panic", t, i, delta)
    return t[:i] + (newval,) + t[i+1:]

def advance(pos: int, move: int) -> int:
    return ((pos - 1) + move) % 10 + 1

def map_index(t: tuple, i: int, f) -> tuple:
    assert 0 <= i < len(t), ("panic", t, i, f)
    return t[:i] + (f(t[i]),) + t[i+1:]

def qgame(
    player: int, 
    scores: IntPair, positions: IntPair,
    limit: int,
    path: tuple,
) -> int:
    assert max(scores) < limit, ("panic!", player, scores, positions, limit) 

    curpos = positions[player]
    curscore = scores[player]

    for move in qrolls:
        newpos = advance(curpos, move)
        newscore = curscore + newpos

        if newscore >= limit:
            yield player, path + (move,)
        else:
            yield from (
                qgame(
                   1 - player,
                   replace_index(scores, player, newscore),
                   replace_index(positions, player, newpos),
                   limit,
                   path + (move,),
                )
            )

def star(f): return lambda t: f(*t)
def drain(s):
    for _ in s:
        pass

def every(f, n, s):
    count = 0
    for item in s:
        count += 1
        if count % n == 0:
            f(count, item)
        yield item

def part2(fname: str):
    qwins = [0, 0]
    s = qgame(0, (0, 0), (4, 8), 21, tuple([]))
    # s = islice(s, 40)
    s = every(print, 1000, s)
    for player, moves in s:
        ucount = mul(qmult[m] for m in moves)
        print(player, moves, ucount)

        qwins[player] += ucount

    print(f'part 2: {qwins}')

if __name__ == '__main__':
    # part1(sys.argv[1])
    part2(sys.argv[1])