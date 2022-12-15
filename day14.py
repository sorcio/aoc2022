"""
https://adventofcode.com/2022/day/14
"""

from typing import IO

from aoc import puzzle


@puzzle
def day14(input: IO[str]):
    paths = []
    for line in input:
        key_points = [
            (int(x), int(y))
            for x, y in (point.split(",") for point in line.split(" -> "))
        ]
        paths.append(key_points)
    print(paths)

    START = START_X, START_Y = 500, 0
    E, R, S, X = ["⬜️", "⬛️", "🟠", "🔵"]

    max_x = max(START_X, max(x for points in paths for x, _ in points))
    min_x = min(START_X, min(x for points in paths for x, _ in points))
    max_y = max(START_Y, max(y for points in paths for _, y in points))
    min_y = min(START_Y, min(y for points in paths for _, y in points))
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    assert START_Y == min_y

    print(f"{width = } {height = }")
    
    def grid_set(x: int, y: int, value: str):
        # grid_x = x - min_x
        grid_x = x - offset_x
        grid_y = y - min_y
        grid[grid_y][grid_x] = value

    def grid_get(x: int, y: int) -> str:
        # grid_x = x - min_x
        grid_x = x - offset_x
        grid_y = y - min_y
        return grid[grid_y][grid_x]

    def print_grid():
        for row in grid:
            print("".join(row))
        print()


    # 500 - x = grid_width // 2
    grid_width = width + 2 * height
    offset_x = START_X - grid_width // 2
    grid = [[E] * grid_width for _ in range(height)]
    grid_set(*START, X)

    # needed for part 2, can be ignored in part 1:
    grid.append([E] * grid_width)
    grid.append([R] * grid_width)


    for path in paths:
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            print("segment", (x1, y1), "->", (x2, y2))
            range_x = range(min(x1, x2), 1 + max(x1, x2))
            range_y = range(min(y1, y2), 1 + max(y1, y2))
            for x in range_x:
                for y in range_y:
                    grid_set(x, y, R)

    print_grid()

    # part 1
    dropped_sand = 0
    while True:
        x = START_X
        for y in range(START_Y + 1, max_y + 1):
            for d in (0, -1, +1):
                if grid_get(x + d, y) == E:
                    x = x + d
                    break
            else:
                # nowhere else to go, rest in place
                grid_set(x, y - 1, S)
                dropped_sand += 1
                break
        else:
            break
    
    print_grid()
    print("part 1:", dropped_sand)

    # part 2
    grid = [[x if x in (R, X) else E for x in row] for row in grid]
    
    dropped_sand = 0
    flowing = True
    while flowing:
        x = START_X
        for y in range(START_Y + 1, max_y + 1 + 2):
            for d in (0, -1, +1):
                if grid_get(x + d, y) == E:
                    x = x + d
                    break
            else:
                # nowhere else to go, rest in place
                grid_set(x, y - 1, S)
                dropped_sand += 1
                if (x, y - 1) == START:
                    flowing = False
                break
        else:
            break
    print_grid()
    print("part 2:", dropped_sand)
