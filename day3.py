"""
https://adventofcode.com/2022/day/3
"""

from functools import reduce
from typing import IO

from aoc import puzzle


def prio(x: str) -> int:
    n = ord(x)
    lower = n - ord('a')
    upper = n - ord('A')
    if 0 <= lower <= 26:
        return 1 + lower
    elif 0 <= upper <= 26:
        return 26 + 1 + upper
    else:
        raise ValueError("{x!r} is not a letter")


@puzzle
def day3(input: IO[str]):
    total = 0
    total_part_2 = 0
    triplets = []
    for i, line in enumerate(input, 1):
        items = line.strip()
        assert len(items) % 2 == 0
        comp1 = set(items[:len(items) // 2])
        comp2 = set(items[len(items) // 2:])
        overlap = comp1 & comp2
        assert len(overlap) == 1, f"more than one overlapping item in {comp1} {comp2}"
        item, = overlap
        item_prio = prio(item)
        total += item_prio
        # print(item, item_prio, total)
        # for part 2:
        print(items)
        triplets.append(set(items))
        if i % 3 == 0:
            three_set = reduce(set.intersection, triplets)
            triplets.clear()
            assert len(three_set) == 1, f"more than one badge item in {three_set}"
            item_2, = three_set
            item_2_prio = prio(item_2)
            total_part_2 += item_2_prio
            print(f" {i:4d} {item_2} {item_2_prio} {total_part_2}")
