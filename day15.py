"""
https://adventofcode.com/2022/day/15
"""

import re
from typing import IO, Iterator

from aoc import puzzle


Pos = tuple[int, int]


def manhattan(a: Pos, b: Pos) -> int:
    (ax, ay), (bx, by) = a, b
    return abs(ax - bx) + abs(ay - by)


def parse_input(input: IO[str]) -> Iterator[tuple[Pos, Pos, int]]:
    pattern = re.compile(r"(-?[0-9]+)")
    for line in input:
        coords = map(int, pattern.findall(line))
        sx, sy, bx, by = coords
        distance = manhattan((sx, sy), (bx, by))
        yield (sx, sy), (bx, by), distance


@puzzle
def day15(input: IO[str]):
    sensors = [*parse_input(input)]

    max_x = max(max(sx, bx) for (sx, _), (bx, _), _ in sensors)
    min_x = min(min(sx, bx) for (sx, _), (bx, _), _ in sensors)
    max_y = max(max(sy, by) for (_, sy), (_, by), _ in sensors)
    min_y = min(min(sy, by) for (_, sy), (_, by), _ in sensors)
    print(f"{min_x=} {max_x=} {min_y=} {max_y=}")
    width = max_x - min_x
    height = max_y - min_y
    print(f"{width=} {height=}")
    max_distance = max(d for _, _, d in sensors)

    if width < 30:
        # we are in the example
        ROW = 10
        draw = True
        rows = range(min_y, max_y + 1)
        search_space = range(0, 20 + 1)
    else:
        # actual input
        ROW = 2000000
        draw = False
        rows = range(ROW, ROW + 1)
        search_space = range(0, 4000000 + 1)

    # drawing symbols
    BEACON = "✨"
    SENSOR = "📡"
    COVERED = "⬜️"
    DARK = "⬛️"
    SOS = "🆘"

    distress = None
    if False:
        for y in rows:
            print(f"{y:8} ", end="")
            covered_count = 0
            for x in range(min_x - max_distance, max_x + max_distance + 1):
                is_covered = False
                is_beacon = False
                is_sensor = False
                pos = (x, y)
                for sensor, beacon, distance in sensors:
                    if sensor == pos:
                        is_sensor = True
                    if beacon == pos:
                        is_beacon = True
                    if manhattan(sensor, pos) <= distance:
                        is_covered = True
                        # break
                if is_beacon:
                    assert is_covered
                    c = BEACON
                elif is_sensor:
                    c = SENSOR
                elif is_covered:
                    covered_count += 1
                    c = COVERED
                else:
                    if x in search_space and y in search_space:
                        c = SOS
                        distress = x, y
                    else:
                        c = DARK
                if draw:
                    print(c, end="")
            print(" ", covered_count)

    # if distress:
    #     print("found source of distress signal at", distress)
    #     tuning_freq = distress[0] * 4000000 + distress[1]
    #     print("tuning frequency =", tuning_freq)

    def merge_segments(segs: list[tuple[int, int]]):
        if not segs:
            return
        start = segs[0][0]
        end = segs[0][1]
        for x0, x1 in segs:
            if x0 > end + 1:
                yield start, end
                start = x0
                end = x1
            elif x1 > end:
                end = x1
        yield start, end

    print("--------------------")
    for y in range(-12, 28):
        # for y in rows:
        print(f"{y:8} ", end="")
        segments = []
        beacons_on_row = set()
        sensors_on_row = []
        for (sx, sy), (bx, by), distance in sensors:
            if by == y:
                beacons_on_row.add(bx)
            if sy == y:
                sensors_on_row.append(sx)
            dy = abs(sy - y)
            if dy <= distance:
                dx = distance - dy
                segments.append((sx - dx, sx + dx))

        segments.sort()

        covered_count = 0
        x_left = min_x - max_distance
        x_right = max_x + max_distance
        if draw:
            drawing = [DARK] * (x_right - x_left + 1)
        else:
            drawing = []

        for x0, x1 in merge_segments(segments):
            segment_length = x1 - x0 + 1
            covered_count += segment_length
            if draw:
                drawing[x0 - x_left : x1 - x_left + 1] = [COVERED] * segment_length

        if draw:
            for bx in beacons_on_row:
                drawing[bx - x_left] = BEACON
            for sx in sensors_on_row:
                drawing[sx - x_left] = SENSOR
            print("".join(drawing), end="")

        covered_count -= len(sensors_on_row) + len(beacons_on_row)
        print(" ", covered_count)

    print("--------------------")
    # coordinate change
    # w = x + y
    # z = x - y
    #
    # x = (w + z) / 2
    # y = (w - z) / 2
    #
    # note that manhattan distance in XY becomes chebyshev distance in WZ but
    # i'm not sure i know how i proved this.
    # manhattan(a,b) = sum(abs(xa - xb) for xa, xb in zip(a, b))
    # chebyshev(a,b) = max(abs(xa - xb) for xa, xb in zip(a, b))

    sensors_wz = []
    for (sx, sy), (bx, by), distance in sensors:
        sw = sx + sy
        sz = sx - sy
        bw = bx + by
        bz = bx - by
        distance_wz = max(abs(sw - bw), abs(sz - bz))
        assert distance_wz == distance
        sensors_wz.append(((sw, sz), (bw, bz), distance_wz))

    ws = sorted(
        set(
            w
            for (sw, sz), _, distance in sensors_wz
            for w in (sw - distance - 1, sw + distance + 1)
            if (w + sz) // 2 in search_space and (w - sz) // 2 in search_space
        )
    )

    # sort by sz - distance (needed by merge)
    sensors_wz.sort(key=lambda s: s[0][1] - s[2])

    for w in ws:
        segments = []
        # This is a quadratic bottleneck but input set is so small that it's
        # fast enough. If len(sensors) were very large it could be replaced by
        # some kind of spatial index lookup.
        for (sw, sz), beacon, distance in sensors_wz:
            if abs(sw - w) <= distance:
                segments.append((sz - distance, sz + distance))
        if not segments:
            continue
        merged = merge_segments(segments)
        try:
            _, z0 = next(merged)
            z1, _ = next(merged)
            print(f"found gap at wz ({w},{z0}-{z1})")
            assert z1 - z0 == 2, "gap wider than 1 cell"
            gap_z = z0 + 1
            x = (w + gap_z) // 2
            y = (w - gap_z) // 2
            distress = (x, y)
            break
        except StopIteration:
            pass

    if draw:
        min_w = min_x + min_y - 8
        max_w = max_x + max_y
        min_z = min_x - max_y
        max_z = max_x - min_y + 4

        def chebyshev(a: Pos, b: Pos) -> int:
            return max(abs(ai - bi) for ai, bi in zip(a, b))

        for w in range(min_w, max_w):
            for z in range(min_z, max_z):
                is_covered = False
                is_beacon = False
                is_sensor = False
                pos = (w, z)
                for sensor, beacon, distance in sensors_wz:
                    if sensor == pos:
                        is_sensor = True
                    if beacon == pos:
                        is_beacon = True
                    if chebyshev(sensor, pos) <= distance:
                        is_covered = True
                true_cell = (w + z) % 2 == 0
                if is_beacon:
                    assert is_covered
                    c = BEACON
                elif is_sensor:
                    c = SENSOR
                elif is_covered:
                    c = COVERED if true_cell else "🟨"
                else:
                    x = (w + z) // 2
                    y = (w - z) // 2
                    if x in search_space and y in search_space:
                        c = SOS
                        distress = x, y
                    else:
                        c = DARK if true_cell else "🟫"
                if draw:
                    print(c, end="")
            print()
    if distress:
        print("found source of distress signal at", distress)
        tuning_freq = distress[0] * 4000000 + distress[1]
        print("tuning frequency =", tuning_freq)


if __name__ == "__main__":
    day15.run_puzzle()
