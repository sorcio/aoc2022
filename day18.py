"""
https://adventofcode.com/2022/day/18
"""

from enum import Enum
from typing import IO, Collection, Iterator

from aoc import puzzle


@puzzle
def day18(input: IO[str]):
    Pos = tuple[int, int, int]
    AIR, LAVA, FLOOD, OUT = B = Enum("B", names="AIR LAVA FLOOD OUT")

    # we add some padding to make flood filling from the outside easier
    blocks: list[Pos] = [tuple(int(x) + 1 for x in line.split(",")) for line in input]

    max_x, max_y, max_z = [max(block[i] for block in blocks) for i in range(3)]
    min_pos = [min(block[i] for block in blocks) for i in range(3)]
    assert all(x > 0 for x in min_pos)

    # some comfy padding here as well
    volume = [
        [[AIR for _ in range(max_x + 2)] for _ in range(max_y + 2)]
        for _ in range(max_z + 2)
    ]

    for x, y, z in blocks:
        volume[z][y][x] = LAVA

    def get(x: int, y: int, z: int) -> B:
        if x < 0 or y < 0 or z < 0 or x > max_x + 1 or y > max_y + 1 or z > max_z + 1:
            return OUT
        return volume[z][y][x]

    def neighbors(pos: Pos) -> Iterator[Pos]:
        for dir in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            for sign in (-1, +1):
                yield tuple(x + dx * sign for x, dx in zip(pos, dir))

    exposed_faces = 0
    for block in blocks:
        for nx, ny, nz in neighbors(block):
            if get(nx, ny, nz) != LAVA:
                exposed_faces += 1

    print("part 1", exposed_faces)

    # part 2

    start = (0, 0, 0)
    queue: list[Pos] = [start]
    outside_exposed_faces = 0
    while queue:
        x, y, z = pos = queue.pop(0)
        # print(x, y, z, get(x, y, z))
        if get(x, y, z) != AIR:
            continue
        volume[z][y][x] = FLOOD
        for nx, ny, nz in neighbors(pos):
            # print("    * ", nx, ny, nz, get(nx, ny, nz))
            match get(nx, ny, nz):
                case B.AIR:
                    queue.append((nx, ny, nz))
                case B.OUT:
                    pass
                case B.LAVA:
                    outside_exposed_faces += 1
                case B.FLOOD:
                    pass
    print("part 2", outside_exposed_faces)


def export_volume(
    blocks: Collection[tuple[int, int, int]], filename: str = "model_day18.vox"
):
    max_dims = [max(block[i] for block in blocks) for i in range(3)]
    min_dims = [min(block[i] for block in blocks) for i in range(3)]
    size_dims = [mx - mn for mx, mn in zip(max_dims, min_dims)]
    model_size = len(blocks)

    from struct import Struct

    header = Struct("<4si")
    chunk_header = Struct("<4sii")
    size_chunk_struct = Struct("<iii")
    size_chunk_content = size_chunk_struct.pack(*size_dims)
    size_chunk_header = chunk_header.pack(b"SIZE", len(size_chunk_content), 0)
    xyzi_data_size = 4 * model_size
    xyzi_chunk_size = 4 + xyzi_data_size
    xyzi_chunk_header = chunk_header.pack(b"XYZI", xyzi_chunk_size, 0)
    main_data_size = (
        len(size_chunk_content)
        + len(size_chunk_header)
        + len(xyzi_chunk_header)
        + xyzi_chunk_size  # xyzi content
    )
    main_chunk_header = chunk_header.pack(b"MAIN", 0, main_data_size)
    voxel_struct = Struct("<BBBB")
    with open(filename, "wb") as f:
        f.write(header.pack(b"VOX ", 150))
        f.write(main_chunk_header)
        f.write(size_chunk_header)
        f.write(size_chunk_content)
        f.write(xyzi_chunk_header)
        f.write(model_size.to_bytes(4, "little"))
        for voxel in blocks:
            f.write(voxel_struct.pack(*voxel, 2))


if __name__ == "__main__":
    day18.run_puzzle()
