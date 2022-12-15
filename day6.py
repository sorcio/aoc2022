"""
https://adventofcode.com/2022/day/6
"""

from collections import deque
from typing import IO

from aoc import puzzle


def find_marker(input: IO[str], length: int) -> tuple[int, str]:
    window: deque[str] = deque(maxlen=length)
    pos = 0
    while True:
        c = input.read(1)
        if not c:
            raise EOFError
        window.append(c)
        pos += 1
        if len(window) == length and len(set(window)) == length:
            return pos, ''.join(window)


@puzzle
def day6(input: IO[str]):
    pos, marker = find_marker(input, 4)
    print(f"marker after {pos} chars: {marker}")
    pos2, marker2 = find_marker(input, 14)
    print(f"second marker after {pos2} chars: {marker2}")
    print(f"absolute pos: {pos + pos2}")


if __name__ == "__main__":
    day6.run_puzzle()
