"""
https://adventofcode.com/2022/day/7
"""

from collections import defaultdict
from typing import IO

from aoc import puzzle


@puzzle
def day7(input: IO[str]):
    cwd: tuple[str, ...] = ()
    fs: dict[tuple[str, ...], dict[str, int]] = defaultdict(dict)
    for raw_line in input:
        line = raw_line.strip()
        if line == "$ cd ..":
            cwd = cwd[:-1]
        elif line == "$ cd /":
            cwd = ()
        elif line.startswith("$ cd "):
            arg = line.removeprefix("$ cd ")
            cwd = (*cwd, arg)
        elif line == "$ ls":
            pass
        elif line.startswith("dir "):
            pass
        else:
            _size, _, name = line.partition(" ")
            size = int(_size)
            # directory = fs.setdefault(cwd, {})
            directory = fs[cwd]
            assert name not in directory
            directory[name] = size
    
    print(fs)

    sizes = defaultdict(int)
    for path, entries in fs.items():
        for i in range(0, 1 + len(path)):
            partial_path = path[:i]
            for size in entries.values():
                sizes[partial_path] += size
            print(partial_path, sizes[partial_path])

    print("--------------------------")

    total_size = 0
    for path, size in sizes.items():
        # note: part 1 ignores the root directory
        if path and size <= 100000:
            total_size += size
        print(path, size, total_size)
    
    print("part 1", total_size)

    print()

    # part 2

    disk_space = 70000000
    target_free = 30000000
    used = sizes[()]
    free = disk_space - used
    assert target_free > free, "already have enough space"
    to_free = target_free - free

    sizes_sorted = sorted(sizes.values())
    for size in sizes_sorted:
        if size >= to_free:
            print("part 2", size)
            break
