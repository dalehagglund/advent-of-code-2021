import sys
import typing as ty
from dataclasses import dataclass

N = 1000

grid = [ [0] * N for _ in range(N) ]

@dataclass
class Point:
    x: int
    y: int

def read_vectors(fname) -> ty.List[Point]:
    vectors = []
    with open(fname) as f:
        for line in f:
            left, right = line.split(" -> ")
            x0, y0 = map(int, left.split(","))
            x1, y1 = map(int, right.split(","))
            vectors.append( (Point(x0, y0), Point(x1, y1)) )
    return vectors

def mark(grid, start, end, diag=False):
    x0, y0 = start.x, start.y
    x1, y1 = end.x, end.y

    if x0 == x1:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            grid[x0][y] += 1
    elif y0 == y1:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            grid[x][y0] += 1
    elif diag:
        dx = +1 if x1 >= x0 else -1
        dy = +1 if y1 >= y0 else -1
        x, y = x0, y0
        while True:
            grid[x][y] += 1
            if (x, y) == (x1, y1):
                break
            x, y = x + dx, y + dy

def print_grid():
    def encode(count):
        if count == 0: return "."
        return str(count)
    print("\n".join(
        " ".join(f"{encode(n):>3}" for n in row[:10])
        for row in grid[:10]
    ))

def count_overlaps():
    overlaps = 0    
    for x in range(N):
        for y in range(N):
            if grid[x][y] > 1:
                overlaps += 1
    return overlaps

def part1(fname):
    print("===== PART 1")
    segments = read_vectors(fname)
    for start, end in segments:
        mark(grid, start, end)
    print(f"overlaps: {count_overlaps()}")

def part2(fname):
    print("===== PART 2")
    segments = read_vectors(fname)
    for start, end in segments:
        mark(grid, start, end, diag=True)
    # print_grid()
    print(f"overlaps: {count_overlaps()}")

if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])