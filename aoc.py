from pathlib import Path
from typing import IO, Callable
import requests


INPUTS_DIR = Path("inputs")
SESSION_PATH = Path(".sessionid")


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
    
    # very naive parser: we expect path to be `something/aocYEAR/dayN.py`
    try:
        day = int(path.name.removeprefix("day").removesuffix(".py"))
    except ValueError:
        raise ValueError("only file names like 'day12.py' are supported") from None

    try:
        year = int(path.parent.name.removeprefix("aoc"))
    except ValueError:
        raise ValueError("only paths like `aoc2022/day12.py' are supported") from None
    
    print(f"AOC {year} puzzle {day}")
    print("Getting inputs...", end=" ", flush=True)
    inputs = get_aoc_input(day, year)
    print("done!")
    print("Running puzzle code...")
    print()
    f(inputs)
    print()
    print("All done.")


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
