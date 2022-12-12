"""
https://adventofcode.com/2022/day/5
"""

from typing import IO

from aoc import puzzle


@puzzle
def day5(input: IO[str]):
    stacks: list[list[str]] = []
    for raw_line in input:
        line = raw_line.strip("\n")
        if not line:
            break
        stack_count = len(raw_line) // 4
        if not stacks:
            stacks.extend([] for _ in range(stack_count))
        else:
            assert len(stacks) == stack_count
        for i in range(stack_count):
            crate = line[1 + i * 4:][0]
            if crate.isnumeric():
                break
            elif crate != " ":
                stacks[i].insert(0, crate)

    print(stacks)

    stacks = [s[:] for s in stacks]

    puzzle_part = 2

    for raw_line in input:
        _move, _count, _from, _src, _to, _dst  = raw_line.split()
        assert ((_move, _from, _to) == ("move", "from", "to"))
        count = int(_count)
        src = int(_src) - 1
        dst = int(_dst) - 1
        if puzzle_part == 1:
            for _ in range(count):
                stacks[dst].append(stacks[src].pop())
        elif puzzle_part == 2:
            tmp_stack = []
            for _ in range(count):
                tmp_stack.append(stacks[src].pop())
            while tmp_stack:
                stacks[dst].append(tmp_stack.pop())
    
    print(stacks)
    print("".join(s[-1] for s in stacks))
