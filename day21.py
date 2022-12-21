"""
https://adventofcode.com/2022/day/21
"""

from collections import defaultdict
from graphlib import TopologicalSorter
from typing import IO

from aoc import puzzle


@puzzle
def day21(input: IO[str]):
    rules = {}
    dag = defaultdict(set)
    for line in input:
        label, _, args = line.strip().partition(": ")
        match args.split():
            case (n,):
                rules[label] = "const", int(n)
            case operand1, op, operand2:
                rules[label] = op, operand1, operand2
                dag[label].add(operand1)
                dag[label].add(operand2)
            case _:
                raise ValueError

    topo = TopologicalSorter(dag)
    table = {}
    for label in topo.static_order():
        match rules[label]:
            case "const", n:
                table[label] = n
            case "-", o1, o2:
                table[label] = table[o1] - table[o2]
            case "+", o1, o2:
                table[label] = table[o1] + table[o2]
            case "*", o1, o2:
                table[label] = table[o1] * table[o2]
            case "/", o1, o2:
                assert table[o1] % table[o2] == 0
                table[label] = table[o1] // table[o2]

    print("part 1", table["root"])


if __name__ == "__main__":
    day21.run_puzzle()
