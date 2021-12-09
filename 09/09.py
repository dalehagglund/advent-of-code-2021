import sys

def read_array(fname):
    with open(fname) as f:
        grid = [
            list(map(int, line.strip()))
            for line in f
        ]
    return len(grid), len(grid[0]), grid

def neighbours(nrow, ncol, row, col):
    if row > 0:
        yield row - 1, col
    if col > 0:
        yield row, col - 1
    if col < ncol - 1:
        yield row, col + 1
    if row < nrow - 1:
        yield row + 1, col

def lowpoints(grid, nrow, ncol):
    for row in range(nrow):
        for col in range(ncol):
            if all(
                grid[row][col] < grid[nr][nc]
                for nr, nc in neighbours(nrow, ncol, row, col)
            ):
                yield row, col 
def part1(fname):
    nrow, ncol, grid = read_array(fname)
    sum = 0
    for row, col in lowpoints(grid, nrow, ncol):
        sum += grid[row][col] + 1
    print("part 1:", sum)

def printgrid(grid, nrow, ncol):
    print("\n".join(
        " ".join(f'{grid[r][c]:3d}' for c in range(ncol))
        for r in range(nrow)
    ))

def find_basin(tag, basins, grid, nrow, ncol, sr, sc, depth=0):
    basins[sr][sc] = tag
    h = grid[sr][sc]
    # print("> " * depth, f"{sr = } {sc = }")
    yield sr, sc
    for nr, nc in neighbours(nrow, ncol, sr, sc):
        # print("> " * depth, f"{nr = } {nc = }")
        if grid[nr][nc] == 9:
            continue
        if basins[nr][nc] == tag:
            continue
        if grid[nr][nc] > h:
            yield from find_basin(tag, basins, grid, nrow, ncol, nr, nc, depth = depth+1)
      
def part2(fname):
    nrow, ncol, grid = read_array(fname)
    sizes = {}
    basins = [ 
        [0] * ncol 
        for _ in range(nrow)
    ]
    # printgrid(grid, nrow, ncol)

    for row in range(nrow):
        for col in range(ncol):
            if grid[row][col] == 9:
                basins[row][col] = -1

    # print(list(find_basin(3, basins, grid, nrow, ncol, 0, 1)))
    # for br, bc in find_basin(3, basins, grid, nrow, ncol, 0, 0):
    #     print((br, bc)


    lows = lowpoints(grid, nrow, ncol)
    sizes = [
        len(list(find_basin(i + 1, basins, grid, nrow, ncol, lr, lc)))
        for i, (lr, lc) in enumerate(lows)
    ]
    # for i, (row, col) in enumerate(lowpoints(grid, nrow, ncol)):
    #     cells = list(find_basin(i + 1, basins, grid, nrow, ncol, row, col))
    #     print(f'lowpoint ({row}, {col}) basin size {len(cells)}')
    from operator import mul
    from functools import reduce
    print("part 2:", reduce(mul, sorted(sizes)[-3:]))

if __name__ == '__main__':
    part1(sys.argv[1])        
    part2(sys.argv[1])        
