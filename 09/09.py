import sys

def read_array(fname):
    with open(fname) as f:
        grid = [
            list(map(int, line.strip()))
            for line in f
        ]
    return len(grid), len(grid[0]), grid

def neighbours(nrow, ncol, row, col):
    if row > 0:        yield row - 1, col
    if col > 0:        yield row, col - 1
    if col < ncol - 1: yield row, col + 1
    if row < nrow - 1: yield row + 1, col

def low_points(grid, nrow, ncol):
    for row in range(nrow):
        for col in range(ncol):
            if all(
                grid[row][col] < grid[nr][nc]
                for nr, nc
                in neighbours(nrow, ncol, row, col)
            ):
                yield row, col 

def part1(fname):
    nrow, ncol, grid = read_array(fname)
    total_risk = 0
    for row, col in low_points(grid, nrow, ncol):
        total_risk += grid[row][col] + 1
    print("part 1:", total_risk)

def print_grid(grid, nrow, ncol):
    print("\n".join(
        " ".join(f'{grid[r][c]:3d}' for c in range(ncol))
        for r in range(nrow)
    ))

def make_grid(nrow, ncol, fill=0):
    return [ [fill] * ncol for _ in range(nrow) ]

def find_basin(tag, basins, grid, nrow, ncol, sr, sc, depth=0):
    basins[sr][sc] = tag
    h = grid[sr][sc]

    yield sr, sc
    for nr, nc in neighbours(nrow, ncol, sr, sc):
        if grid[nr][nc] == 9: continue
        if basins[nr][nc] == tag: continue
        if grid[nr][nc] > h:
            yield from find_basin(tag, basins, grid, nrow, ncol, nr, nc, depth = depth+1)
      
def part2(fname):
    nrow, ncol, grid = read_array(fname)
    basins = make_grid(nrow, ncol, 0)
    
    lows = low_points(grid, nrow, ncol)
    sizes = sorted(
        len(list(
            find_basin(
                i + 1, basins, grid, nrow, ncol, lr, lc)))
        for i, (lr, lc) in enumerate(lows)
    )

    from operator import mul
    from functools import reduce
    print("part 2:", reduce(mul, sizes[-3:]))

if __name__ == '__main__':
    part1(sys.argv[1])        
    part2(sys.argv[1])        
