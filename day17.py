"""
https://adventofcode.com/2022/day/17
"""

from dataclasses import dataclass
from itertools import cycle, islice
from typing import IO, Sequence

from aoc import puzzle

PIECES_SOURCE = """
####

.#.
###
.#.

..#
..#
###

#
#
#
#

##
##
"""


Shape = tuple[tuple[bool, ...], ...]


class Piece:
    def __init__(self, shape: Shape):
        width = len(shape[0])
        assert all(len(row) == width for row in shape)
        height = len(shape)

        bottom_contour = [
            height - max(y for y in range(height) if shape[y][x]) - 1
            for x in range(width)
        ]
        left_contour = [min(x for x in range(width) if row[x]) for row in shape]
        right_contour = [max(x for x in range(width) if row[x]) for row in shape]

        self.shape = shape
        self.width = width
        self.height = height
        self.bottom_contour = bottom_contour
        self.left_contour = left_contour
        self.right_contour = right_contour

    def blocks(self):
        for y, row in enumerate(self.shape):
            for x, b in enumerate(row):
                if b:
                    yield x, (self.height - y - 1)

    def __repr__(self):
        r = " ".join("".join("#" if b else "." for b in row) for row in self.shape)
        return f"<{r}>"


def load_pieces(source: str) -> tuple[Piece, ...]:
    piece: list[tuple[bool, ...]] = []
    pieces: list[Piece] = []
    for line in source.splitlines() + [""]:
        if line:
            piece.append(tuple(c == "#" for c in line))
        elif piece:
            pieces.append(Piece(tuple(piece)))
            piece = []
    return tuple(pieces)


PIECES = load_pieces(PIECES_SOURCE)


class Field:
    BREADTH = range(7)
    COLORS = ["🟦", "🟧", "🟩", "🟨", "🟪"]

    def __init__(self):
        # rows start at the bottom, i.e. y = 0 is bottom line
        self.data: list[list[int]] = []
        self._colors = cycle(range(1, 1 + len(Field.COLORS)))

    @property
    def height(self) -> int:
        return len(self.data)

    def has_block(self, x: int, y: int) -> bool:
        if x not in Field.BREADTH:
            raise ValueError(f"x must be in [0,7), not {x!r}")
        if y < 0:
            raise ValueError(f"y must be >= 0, not {y!r}")
        try:
            return self.data[y][x] != 0
        except IndexError:
            return False

    def collides(self, piece: Piece, x: int, y: int) -> bool:
        for bx, by in piece.blocks():
            field_x = bx + x
            field_y = by + y
            if field_x not in Field.BREADTH:
                return True
            if field_y < 0:
                return True
            if self.has_block(field_x, field_y):
                return True
        return False

    def drop(self, piece: Piece, x: int, y: int) -> None:
        color = next(self._colors)
        for bx, by in piece.blocks():
            field_x = bx + x
            field_y = by + y
            new_rows = field_y - self.height + 1
            self._extend(new_rows)
            assert self.data[field_y][field_x] == 0
            # self.data[field_y][field_x] = color
            self.data[field_y][field_x] = 1

    def _extend(self, rows: int):
        for _ in range(rows):
            self.data.append([0] * len(self.BREADTH))

    def draw(self):
        for y in range(self.height)[::-1]:
            line = "".join(Field.COLORS[x - 1] if x else "⬛️" for x in self.data[y])
            print(line)


@puzzle
def day17(input: IO[str]):
    jets = (*filter(None, ({">": +1, "<": -1}.get(c) for c in next(input))),)

    print(f"{len(jets) = } {len(PIECES) = }")

    _, field1 = simulate(PIECES, jets, 2022)
    print("part 1:", field1.height)

    # part 2
    #
    # terrible, terrible approach but it works, and I didn't have to rewrite
    # the simulation. let's do it right another time maybe

    PART_2_N = 1000000000000
    _, field2 = simulate(PIECES, jets, 10000)

    def render_row(row):
        return "".join("🟦" if x else "⬛️" for x in row)

    def find_repeats(data):
        print(f"{len(data)=}")
        for i1 in range(len(data)):
            for size in range(2, len(data) - i1 - 1):
                repeats = (len(data) - i1 - 1) // size - 1
                if not repeats:
                    break
                # print(i1, "size", size, "times", repeats)
                for n in range(repeats):
                    for i in range(size):
                        if data[i1 + size * n + i] != data[i1 + size * (n + 1) + i]:
                            break
                    else:
                        # print("maybe", i1, size, n)
                        continue
                    # print("nope", i1, size, n)
                    break
                else:
                    print(i1, size, "good")
                    # print("\n".join(render_row(r) for r in data[i1:i1+size][::-1]))
                    # print()
                    # print("\n".join(render_row(r) for r in data[i1+size:i1+2*size][::-1]))
                    return i1, size
                # print()
        raise RuntimeError

    initial, period = find_repeats(field2.data)

    # print(f"{initial%len(PIECES)=} {period%len(PIECES)=}")
    
    # print("\n".join(render_row(r) for r in field2.data[:initial][::-1]))
    # print()
    # print("\n".join(render_row(r) for r in field2.data[initial:initial+period][::-1]))
    # print()
    # print("\n".join(render_row(r) for r in field2.data[initial+period:initial+2*period][::-1]))

    print()
    n, field = simulate(PIECES, jets, 10000, stop_at_height=initial)
    print("n ", n, field.height, field.height == initial)
    n2, field = simulate(PIECES, jets, 10000, stop_at_height=initial+period)
    print("n2", n2, field.height, field.height == initial + period)

    prev = n2
    period_in_drops = -1
    # just to double-check, okay?
    for i in range(2, 10):
        stop_at_height = initial + i * period
        n2b, field = simulate(PIECES, jets, prev * 4, stop_at_height=stop_at_height)
        assert field.height == stop_at_height
        period_in_drops = n2b - prev
        print("  ", n2b, field.height, field.height == initial + i * period, period_in_drops)
        prev = n2b

    # we know that the first `initial+period` height is done in `n2` drops
    # we know that each additional `period_in_drops` drops add `period` height

    print(f"{initial = }")
    print(f"{period = }")
    print(f"{initial+period = }")
    print(f"{n2 = }")

    times, remainder = divmod(PART_2_N - n2, period_in_drops)
    print(f"{PART_2_N - n2 = } = {times} * {period_in_drops} + {remainder}")
    K = 2
    n3, field = simulate(PIECES, jets, n2 + remainder + K * period_in_drops, stop_at_height=20000)
    print("remainder", remainder, "n3", n3, field.height)
    assert n3 == remainder + n2 + K * period_in_drops
    remaninder_height = field.height - initial - K * period
    print("remainder_height", remaninder_height)

    height = initial + period * times + remaninder_height
    print("part 2:", height)


def simulate(pieces: Sequence[Piece], jets: Sequence[int], n: int, draw: bool = False, stop_at_height: int = 10000):
    iter_pieces = cycle(iter(pieces))
    iter_jets = cycle(iter(jets))
    field = Field()
    dropped_pieces = 0
    base = 0
    for piece in islice(iter_pieces, n):
        # position always refers to bottom-right corner of piece
        x = 2
        y = field.height + 3

        # field.drop(piece, x, y)
        # field.draw()
        # return
        # Note: starting pos is always collision-free by definition
        falling = True
        while falling:
            # first: (attempt to) move left/right according to stream
            push = next(iter_jets)
            new_x = x + push
            if not field.collides(piece, new_x, y):
                x = new_x

            # next: drop down one row
            new_y = y - 1
            if field.collides(piece, x, new_y):
                field.drop(piece, x, y)
                falling = False
            else:
                y = new_y

        if draw and field.height < 30:
            field.draw()
            print(field.height)
            print()

        dropped_pieces += 1
        if field.height >= stop_at_height:
            break
        # if all(field.data[-1]):
        #     print(field.height, dropped_pieces)
        #     base += field.height
        #     dropped_pieces = 0
        #     field = Field()

    return dropped_pieces, field


if __name__ == "__main__":
    day17.run_puzzle()
