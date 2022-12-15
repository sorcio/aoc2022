"""
https://adventofcode.com/2022/day/11
"""

from typing import IO, Callable, Iterator, NamedTuple

from aoc import puzzle


class Monkey(NamedTuple):
    items: list[int]
    update: Callable[[int], int]
    divisible_by: int
    throw_to: tuple[int, int]


def parse_monkey(input: Iterator[str]) -> Monkey:
    items = [
        int(x) for x in next(input).strip().removeprefix("Starting items: ").split(", ")
    ]
    op_line = next(input).strip().removeprefix("Operation: ")
    _new, _eq, _old, op, right = op_line.split()
    assert (_new, _eq, _old) == ("new", "=", "old")
    test = int(next(input).strip().removeprefix("Test: divisible by "))
    if_true = int(next(input).strip().removeprefix("If true: throw to monkey "))
    if_false = int(next(input).strip().removeprefix("If false: throw to monkey "))

    op_func = {
        "+": int.__add__,
        "*": int.__mul__,
    }[op]

    if right == "old":
        update = lambda old: op_func(old, old)
    else:
        n = int(right)
        update = lambda old: op_func(old, n)

    return Monkey(items, update, test, (if_false, if_true))


@puzzle
def day11(input: IO[str]):
    monkeys: list[Monkey] = []
    for line in input:
        if line.startswith("Monkey "):
            monkeys.append(parse_monkey(input))

    # ROUNDS, REDUCTION = 20, 3  # part 1
    ROUNDS, REDUCTION = 10000, 1  # part 2

    modulo = 1
    for monkey in monkeys:
        modulo *= monkey.divisible_by

    counters = [0 for _ in monkeys]
    for _ in range(ROUNDS):
        for i, monkey in enumerate(monkeys):
            while monkey.items:
                counters[i] += 1
                item = monkey.items.pop(0)
                item = monkey.update(item) // REDUCTION % modulo
                test = item % monkey.divisible_by == 0
                throw_to = monkey.throw_to[test]
                monkeys[throw_to].items.append(item)
    print(counters)
    top2, top1 = sorted(counters)[-2:]
    print("monkey business:", top1 * top2)


if __name__ == "__main__":
    day11.run_puzzle()
