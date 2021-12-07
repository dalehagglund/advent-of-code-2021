import sys

def read_positions(line):
    return list(map(int, line.strip().split(",")))

def part1(fname: str):
    with open(fname) as f:
        positions = read_positions(f.readline())
    lower, upper = min(positions), max(positions)
    minfuel = float("+inf")

    for target in range(lower, upper+1):
        fuel = sum(
            abs(pos - target) for pos in positions
        )
        if fuel < minfuel:
            minfuel = fuel
    print(minfuel)
    
def part2(fname: str):
    with open(fname) as f:
        positions = read_positions(f.readline())
    lower, upper = min(positions), max(positions)
    minfuel = float("+inf")

    for target in range(lower, upper+1):
        def cost(dist: int) -> int:
            return dist * (dist + 1) // 2
        fuel = sum(
            cost(abs(pos - target)) for pos in positions
        )
        if fuel < minfuel:
            minfuel = fuel

    print(minfuel)
    
if __name__ == '__main__':
    part1(sys.argv[1])
    part2(sys.argv[1])