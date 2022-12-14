"""
https://adventofcode.com/2022/day/12
"""

from typing import IO, Iterator

from aoc import puzzle

Pos = tuple[int, int]


def parse_grid(input: Iterator[str]) -> tuple[list[list[int]], Pos, Pos]:
    grid = []
    start, end = None, None
    for r, line in enumerate(input):
        row = []
        for c, char in enumerate(line.strip()):
            if char == "S":
                start = r, c
                char = "a"
            elif char == "E":
                end = r, c
                char = "z"
            assert char.islower()
            height = ord(char) - ord("a")
            row.append(height)
        grid.append(row)
    assert start is not None
    assert end is not None
    return grid, start, end


def shortest_path(
    grid: list[list[int]], start: Pos, end: Pos | None, direction: int = 1
):
    rows = range(len(grid))
    cols = range(len(grid[0]))
    queue: list[tuple[tuple[Pos, ...], Pos]] = [((), start)]
    visited = [[False for _ in row] for row in grid]
    print(f"{start=} {end=}")
    while True:
        steps, (r, c) = queue.pop(0)
        if visited[r][c]:
            continue
        visited[r][c] = True
        # print(f"{len(steps):2}: pos = {r} {c}")
        if (r, c) == end:
            break
        height = grid[r][c]
        if end is None and height == 0:
            break
        # print("    height =", height)
        for step_r, step_c in (-1, 0), (1, 0), (0, -1), (0, 1):
            nr = r + step_r
            nc = c + step_c
            if (
                nr in rows
                and nc in cols
                and not visited[nr][nc]
                and (grid[nr][nc] - height) * direction <= 1
            ):
                # print("       * n", nr, nc, "height", grid[nr][nc])
                new_steps = (*steps, (r, c))
                queue.append((new_steps, (nr, nc)))
    return steps


@puzzle
def day12(input: IO[str]):
    grid, start, end = parse_grid(input)
    steps = shortest_path(grid, start, end)
    print("part 1:", len(steps))
    hiking_steps = shortest_path(grid, end, None, -1)
    print("part 2:", len(hiking_steps))
