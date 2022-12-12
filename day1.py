"""
https://adventofcode.com/2022/day/1
"""

from typing import IO

from aoc import puzzle


@puzzle
def day1(input: IO[str]):
    elves = []
    current_elf = []
    for raw_line in input:
        line = raw_line.strip()
        if line:
            current_elf.append(int(line))
        else:
            elves.append(current_elf)
            current_elf = []
    if current_elf:
        elves.append(current_elf)
    
    print("Part 1")
    print(max(map(sum, elves)))

    print("Part2")
    summed = [*map(sum, elves)]
    summed.sort(reverse=True)
    print(sum(summed[:3]))
