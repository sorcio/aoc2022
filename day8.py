"""
https://adventofcode.com/2022/day/8
"""

from typing import IO, Iterable, Iterator

from aoc import puzzle


@puzzle
def day8(input: IO[str]):
    grid = [[int(x) for x in line.strip()] for line in input]
    rows = range(len(grid))
    cols = range(len(grid[0]))

    def look_at(tiles: Iterable[tuple[int, int]]) -> Iterator[tuple[int, int]]:
        tallest = -1
        for r, c in tiles:
            tree = grid[r][c]
            if grid[r][c] > tallest:
                tallest = tree
                yield r, c

    visible = set()
    for r in rows:
        visible.update(look_at((r, c) for c in cols))
        visible.update(look_at((r, c) for c in reversed(cols)))
    for c in cols:
        visible.update(look_at((r, c) for r in rows))
        visible.update(look_at((r, c) for r in reversed(rows)))

    # print(visible)
    print("part 1 solution", len(visible))

    def visibility(height: int, tiles: Iterable[tuple[int, int]]) -> int:
        i = 0
        for i, (r, c) in enumerate(tiles, 1):
            if grid[r][c] >= height:
                return i
        return i

    # part 2
    best_score = -1
    for row in rows:
        for col in cols:
            h = grid[row][col]
            up = visibility(h, ((r, col) for r in rows[:row][::-1]))
            down = visibility(h, ((r, col) for r in rows[row + 1 :]))
            left = visibility(h, ((row, c) for c in cols[:col][::-1]))
            right = visibility(h, ((row, c) for c in cols[col + 1 :]))
            score = up * down * left * right
            best_score = max(score, best_score)
    print("part 2 solution", best_score)
