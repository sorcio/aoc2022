"""
https://adventofcode.com/2022/day/25
"""

from typing import IO

from aoc import puzzle

SYMBOLS = "=-012"


def from_snafu(x: str) -> int:
    acc = 0
    for c in x:
        acc *= 5
        acc += SYMBOLS.index(c) - 2
    return acc


def to_snafu(x: int) -> str:
    s = ""
    while True:
        q, r = divmod(x + 2, 5)
        s = SYMBOLS[r] + s
        if q == 0:
            return s
        x = q


@puzzle
def day25(input: IO[str]):
    total = 0
    for raw_line in input:
        line = raw_line.strip()
        decoded = from_snafu(line)
        print(line, decoded)
        total += decoded
    print(total, to_snafu(total))


if __name__ == "__main__":
    day25.run_puzzle()
