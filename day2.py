"""
https://adventofcode.com/2022/day/2
"""

from enum import StrEnum
from typing import IO

from aoc import puzzle


Shape = StrEnum('Shape', names='ROCK PAPER SCISSORS')
ROCK, PAPER, SCISSORS = Shape

FIRSTS = dict(zip("ABC", [ROCK, PAPER, SCISSORS]))
SECONDS = dict(zip("XYZ", [ROCK, PAPER, SCISSORS]))
SHAPE_SCORE = {ROCK: 1, PAPER: 2, SCISSORS: 3}
BEATS = {
    ROCK: SCISSORS,
    SCISSORS: PAPER,
    PAPER: ROCK,
}


def get_outcome(first: Shape, second: Shape) -> int:
    if first == second:
        return 3  # draw
    elif BEATS[first] == second:
        return 0  # second lost
    else:
        return 6  # second won


PART1_OUTCOMES = {
    f"{first} {second}": SHAPE_SCORE[second_shape]
    + get_outcome(first_shape, second_shape)
    for first, first_shape in FIRSTS.items()
    for second, second_shape in SECONDS.items()
}

# part 2 stuff
DRAWS = {x: x for x in BEATS}
LOSES = {y: x for x, y in BEATS.items()}
STRATEGY = {"X": BEATS, "Y": DRAWS, "Z": LOSES}


def get_part2_outcome(shape: Shape, strategy: dict[Shape, Shape]) -> int:
    second_shape = strategy[shape]
    # recomputing what we know already but I'm lazy
    return SHAPE_SCORE[second_shape] + get_outcome(shape, second_shape)


PART2_OUTCOMES = {
    f"{first} {second}": get_part2_outcome(first_shape, strategy)
    for first, first_shape in FIRSTS.items()
    for second, strategy in STRATEGY.items()
}


@puzzle
def day2(input: IO[str]):
    total_score = 0
    total_score_part_2 = 0
    for line in input:
        match = line.strip()
        outcome = PART1_OUTCOMES[match]
        total_score += outcome
        outcome_part_2 = PART2_OUTCOMES[match]
        total_score_part_2 += outcome_part_2
        print(match, outcome, total_score, outcome_part_2, total_score_part_2)
