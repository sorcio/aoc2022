"""
https://adventofcode.com/2022/day/20
"""

from typing import IO

from aoc import puzzle


@puzzle
def day20(input: IO[str]):
    cipher = [int(x) for x in input]

    print("part 1\n------------------------------")
    decrypt(cipher)

    print("part 2\n------------------------------")
    KEY = 811589153
    RUNS = 10
    cipher2 = [x * KEY for x in cipher]
    decrypt(cipher2, RUNS)


def decrypt(cipher: list[int], runs: int = 1):
    length = len(cipher)
    positions = [*range(len(cipher))]

    print(f"{length=}")

    def get_plain():
        l = [999999999999] * length
        for c, pos in zip(cipher, positions):
            l[pos] = c
        return l

    # print(get_plain())
    for _ in range(runs):
        for i, (pos, shift) in enumerate(zip(positions, cipher)):
            # print("shift", shift)
            new_pos = (pos + shift - 1) % (length - 1) + 1

            # print(f"{pos} -> {new_pos}")
            if new_pos > pos:
                s = -1
                r = range(pos, new_pos + 1)
            else:
                s = 1
                r = range(new_pos, pos + 1)

            # print(r, s)

            for i2, x in enumerate(positions):
                if x in r:
                    positions[i2] += s

            positions[i] = new_pos

            # print(get_plain())

    plain = get_plain()
    index_zero = plain.index(0)
    print(f"{plain[(index_zero + 1000) % length]}")
    print(f"{plain[(index_zero + 2000) % length]}")
    print(f"{plain[(index_zero + 3000) % length]}")
    print(
        "decrypted:",
        plain[(index_zero + 1000) % length]
        + plain[(index_zero + 2000) % length]
        + plain[(index_zero + 3000) % length],
    )


if __name__ == "__main__":
    day20.run_puzzle()
