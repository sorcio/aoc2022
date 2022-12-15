"""
https://adventofcode.com/2022/day/4
"""

from typing import IO

from aoc import puzzle


def contains(range1: tuple[int, int], range2: tuple[int, int]) -> bool:
    """range1 contains range2"""
    a1, b1 = range1
    a2, b2 = range2
    return a1 <= a2 and b1 >= b2


def overlaps(range1: tuple[int, int], range2: tuple[int, int]) -> bool:
    a1, b1 = range1
    a2, b2 = range2
    return (a2 >= a1 and b1 >= a2) or (a1 >= a2 and b2 >= a1)


assert overlaps((4, 88), (88, 88))

@puzzle
def day4(input: IO[str]):
    counter = 0
    counter_part_2 = 0
    for raw_line in input:
        range1, range2 = [
            (int(x), int(y)) for x, y in (r.split("-") for r in raw_line.split(","))
        ]
        if contains(range1, range2) or contains(range2, range1):
            counter += 1
        if overlaps(range1, range2):
            counter_part_2 += 1
        print(range1, range2, counter, counter_part_2)


if __name__ == "__main__":
    day4.run_puzzle()
