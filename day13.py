"""
https://adventofcode.com/2022/day/13
"""

from functools import cmp_to_key
from itertools import zip_longest
import json
from typing import IO

from aoc import puzzle


def compare_packets(left, right) -> int:
    match left, right:
        case [int(l), int(r)]:
            if l == r:
                return 0
            else:
                return -1 if l < r else +1
        case [[*ls], [*rs]]:
            for l, r in zip_longest(ls, rs):
                c = compare_packets(l, r)
                if c != 0:
                    return c
        case [[*ls], int(r)]:
            return compare_packets(ls, [r])
        case [int(l), [*rs]]:
            return compare_packets([l], rs)
        case [None, int(_) | [*_]]:
            return -1
        case [int(_) | [*_], None]:
            return +1
        case [None, None]:
            return 0
        case _:
            assert False
    return 0


assert compare_packets(3, 5) == -1
assert compare_packets(3, 3) == 0
assert compare_packets(5, 3) == +1
assert compare_packets([], []) == 0
assert compare_packets([1], [1]) == 0
assert compare_packets([2], [1]) == +1
assert compare_packets([1], [2]) == -1
assert compare_packets(9, [8]) == +1


@puzzle
def day13(input: IO[str]):
    lines = filter(None, map(str.strip, input))
    good_pairs = []
    DIV1 = [[2]]
    DIV2 = [[6]]
    packets = [DIV1, DIV2]
    for i, (line1, line2) in enumerate(zip(lines, lines), 1):
        left = json.loads(line1)
        right = json.loads(line2)
        packets.append(left)
        packets.append(right)
        cmp = compare_packets(left, right)
        assert cmp != 0
        if cmp == -1:
            good_pairs.append(i)
    print(good_pairs)
    print("part1:", sum(good_pairs))
    # part 2:
    packets.sort(key=cmp_to_key(compare_packets))
    index_1 = packets.index(DIV1) + 1
    index_2 = packets.index(DIV2, index_1) + 1
    print(f"{index_1=} {index_2=}")
    print("part 2:", index_1 * index_2)
