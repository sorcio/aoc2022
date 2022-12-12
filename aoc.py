from pathlib import Path
from typing import IO, Callable
import requests


INPUTS_DIR = Path("inputs")
SESSION_PATH = Path(".sessionid")
TEMPLATE_PATH = Path("aoc.py.template")


def run_puzzle(puzzle: int, year: int, f: Callable[[IO[str]], None]) -> None:
    input = get_aoc_input(puzzle, year)
    f(input)


def puzzle(f: Callable[[IO[str]], None]) -> None:
    import inspect

    frame = inspect.currentframe()
    if frame is None:
        raise Exception("interpreter does not support frame inspection")
    caller = frame.f_back
    assert caller is not None
    path = Path(caller.f_code.co_filename)

    del frame
    del caller

    day, year = _get_day_and_year_from_path(path)

    print(f"AOC {year} puzzle {day}")
    print("Getting inputs...", end=" ", flush=True)
    inputs = get_aoc_input(day, year)
    print("done!")
    print("Running puzzle code...")
    print()
    f(inputs)
    print()
    print("All done.")


def _get_day_and_year_from_path(path: Path) -> tuple[int, int]:
    # note: don't resolve() the path as we might be using symlinks for names
    path = path.absolute()

    # very naive parser: we expect path to be `something/aocYEAR/dayN.py`
    try:
        day = int(path.name.removeprefix("day").removesuffix(".py"))
    except ValueError:
        raise ValueError("only file names like 'day12.py' are supported") from None

    try:
        year = int(path.parent.name.removeprefix("aoc"))
    except ValueError:
        raise ValueError("only paths like `aoc2022/day12.py' are supported") from None

    return day, year


def get_aoc_input(puzzle: int, year: int) -> IO[str]:
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    file_name = f"input_{year}_{puzzle}"
    path = INPUTS_DIR / file_name
    try:
        return path.open("r")
    except FileNotFoundError:
        pass

    url = f"https://adventofcode.com/{year}/day/{puzzle}/input"
    response = get_aoc_url(url)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path.open("r")


def get_aoc_url(url: str) -> requests.Response:
    _check_aoc_url(url)
    cookies = get_cookies()
    return requests.get(url, cookies=cookies)


def _check_aoc_url(url: str):
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme != "https" and parsed.netloc != "adventofcode.com":
        raise Exception(f"URL is not from https://adventofcode.com/: {url!r}")


def get_cookies() -> dict[str, str]:
    session = SESSION_PATH.read_text().strip()
    return {"session": session}


def main():
    import sys

    try:
        puzzle = int(sys.argv[1])
    except (ValueError, IndexError):
        print(f"usage: python {sys.argv[0]} <PUZZLE_DAY>", file=sys.stderr)
        sys.exit(1)

    if not 1 <= puzzle <= 25:
        print(f"{puzzle} is not a valid day for AOC", file=sys.stderr)
        sys.exit(1)

    path = Path(f"day{puzzle}.py")
    day, year = _get_day_and_year_from_path(path)

    if path.is_file():
        import runpy

        runpy.run_path(str(path))
    else:
        template = TEMPLATE_PATH.read_text()
        path.write_text(template.format(DAY=day, YEAR=year))
        print(f"{path} created from template. Run again to run puzzle.")


if __name__ == "__main__":
    main()
