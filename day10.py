"""
https://adventofcode.com/2022/day/10
"""

from functools import partial
from typing import IO, Callable, Iterator

from aoc import puzzle

X = 0
RegFile = list[int]
Op = Callable[[RegFile], None]


def decoder(instructions: Iterator[str]) -> Iterator[Op]:
    def noop(reg: RegFile):
        pass

    def add_x(n: int, reg: RegFile):
        reg[X] += n

    for instruction in instructions:
        match instruction.strip().split():
            case ["noop"]:
                yield noop
            case ["addx", raw_n]:
                n = int(raw_n)
                yield noop
                yield partial(add_x, n)


@puzzle
def day10(input: IO[str]):
    MILESTONES = [x - 1 for x in [20, 60, 100, 140, 180, 220]]
    COLS = 40
    reg = [1]
    total_value = 0
    for cycle, op in enumerate(decoder(input)):
        if cycle in MILESTONES:
            signal_strength = reg[X] * cycle
            total_value += signal_strength
            # print(f"{cycle=} {signal_strength=} {total_value=}")
        hor = cycle % COLS
        lit = reg[X] - 1 <= hor <= reg[X] + 1
        end = "\n" if hor == COLS - 1 else ""
        print("⬜" if lit else "⬛️", end=end)
        op(reg)

    print()
    print("part 1:", total_value)
