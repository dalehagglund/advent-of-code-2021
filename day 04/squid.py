"""
Advent of Code 2021

Day 4: Giant Squid
https://adventofcode.com/2021/day/4
"""


from dataclasses import dataclass, field
import typing as ty
import sys

@dataclass
class Cell:
    label: int
    marked: bool = False

    def __str__(self):
        return f'{self.label}/{"M" if self.marked else "_"}'

class Board:
    _grid: ty.List[ty.List[Cell]]
    def __init__(self, grid: ty.List[ty.List[int]]):
        self._grid = [
            [ Cell(label=label) for label in row ]
            for row in grid
        ]
    def score(self):
        return sum(
            self._grid[row][col].label
            for row in range(5)
            for col in range(5)
            if not self._grid[row][col].marked
        )
    def print(self):
        for row in range(5):
            print(" ".join(
                f"{self._grid[row][col]!s:>5}"
                for col in range(5)
            ))
    def play(self, draw: int):
        for row in range(5):
            for col in range(5):
                if self._grid[row][col].label == draw:
                    self._grid[row][col].marked = True
    def bingo(self):
        for row in range(5):
            if all(self._marked(row, col) for col in range(5)):
                return True
        for col in range(5):
            if all(self._marked(row, col) for row in range(5)):
                return True
        return False
    def _marked(self, row, col):
        return self._grid[row][col].marked

def read_game(name) -> ty.Tuple[ty.List[int], ty.List[Board]]:
    draws, boards = None, []
    with open(name) as f:
        draws = list(map(int, f.readline().strip().split(",")))
        while True:
            line: str = f.readline()
            if line == '':
                break
            grid = [
                list(map(int, line.strip().split()))
                for line
                in (f.readline() for _ in range(5))
            ]
            # print(grid)
            boards.append(Board(grid))
        return draws, boards

def part1(name):
    print('===== PART 1 =====')
    draws, boards = read_game(name)
    for d in draws:
        for b in boards:
            b.play(d)
        if any(b.bingo() for b in boards):
            break        

    winning_board = [b for b in boards if b.bingo()][0]
    print(winning_board.score() * d)

def part2(name):
    print('===== PART 2 =====')
    draws, boards = read_game(name)
    for d in draws:
        non_winning = list(filter(lambda b: not b.bingo(), boards))
        for b in boards:
            b.play(d)
        if all(b.bingo() for b in boards):
            break        

    last_winning_board = non_winning[0]
    print(last_winning_board.score() * d)

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])