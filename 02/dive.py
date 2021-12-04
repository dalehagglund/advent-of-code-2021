

def read_instructions():
    with open("input.txt") as f:
        line: str
        for line in f:
            instr, delta = line.split()
            delta = int(delta)
            yield (instr, delta)

def part1():
    horiz, depth = 0, 0
    for dir, delta in read_instructions():
        if dir == "forward":
            horiz += delta
        elif dir == "down":
            depth += delta
        elif dir == "up":
            depth -= delta
        else:
            assert False, "huh?"
    print(horiz * depth)

def part2():
    aim, horiz, depth = 0, 0, 0
    for dir, delta in read_instructions():
        if dir == "forward":
            horiz += delta
            depth += aim * delta
        elif dir == "down":
            aim += delta
        elif dir == "up":
            aim -= delta
        else:
            assert False, "huh?"
    print(horiz * depth)
