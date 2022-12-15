"""
https://adventofcode.com/2022/day/9
"""

from typing import IO

from aoc import puzzle

DIRS: dict[str, tuple[int, int]] = {
    "U": (0, -1),
    "D": (0, 1),
    "L": (-1, 0),
    "R": (1, 0),
}


def sign(x: int) -> int:
    if x == 0:
        return 0
    elif x > 0:
        return 1
    else:
        return -1


@puzzle
def day9(input: IO[str]):
    ROPE_LENGTH = 10
    START = 0, 0
    body: list[tuple[int, int]] = [START] * ROPE_LENGTH
    visited: set[tuple[int, int]] = {START}

    # only for drawing
    left, right, up, down = 0, 0, 0, 0

    def make_nice_drawings():
        nonlocal left, right, up, down
        left = min(left, *(x for x, _ in body))
        right = max(right, *(x for x, _ in body))
        up = min(up, *(y for _, y in body))
        down = max(down, *(y for _, y in body))
        print()
        for y in range(up - 1, down + 2):
            line = ""
            for x in range(left - 1, right + 2):
                try:
                    index = body.index((x, y))
                except ValueError:
                    index = -1
                if index == 0:
                    line += "🐍"
                elif index >= 0:
                    line += f"{index}\ufe0f\u20e3 "
                elif (x, y) == START:
                    line += "🔵"
                elif (x, y) in visited:
                    line += "⬛️"
                else:
                    line += "⬜️"
            print(line)
        print()

    # make_nice_drawings()
    for n, line in enumerate(input):
        # if n > 100:
        #     print("STOPPING BEFORE END OF INPUT")
        #     break
        # print(f"[{n:04}] {line.strip()}")
        dx, dy = direction = DIRS[line[0]]
        amount = int(line[1:])
        for _ in range(amount):
            # head moves
            x, y = body[0]
            body[0] = x + dx, y + dy
            del x, y
            # tail follows if detached
            for i, ((hx, hy), (tx, ty)) in enumerate(zip(body, body[1:]), 1):
                distx = hx - tx
                disty = hy - ty
                if max(abs(distx), abs(disty)) > 1:
                    step_x = sign(distx)
                    step_y = sign(disty)
                    body[i] = tx + step_x, ty + step_y
            visited.add(body[-1])
            # make_nice_drawings()

    # print(visited)
    print("visited:", len(visited))


if __name__ == "__main__":
    day9.run_puzzle()
