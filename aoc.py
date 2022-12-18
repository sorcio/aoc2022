# pyright: strict
from functools import partial
from os import getenv
from pathlib import Path
from time import perf_counter_ns
from types import ModuleType
from typing import IO, Callable, NoReturn, Protocol, cast, runtime_checkable
import sys


INPUTS_DIR = Path("inputs")
SESSION_PATH = Path(".sessionid")
TEMPLATE_PATH = Path("aoc.py.template")
INPUT_FILE_TEMPLATE = "input_{year}_{puzzle}.txt"
EXAMPLE_FILE_TEMPLATE = "input_{year}_{puzzle}.example.txt"

PuzzleFunc = Callable[[IO[str]], None]


@runtime_checkable
class Puzzle(Protocol):
    def __call__(self, __input: IO[str]) -> None:
        ...

    def run_puzzle(self, use_example: bool | None = None) -> None:
        ...


def run_puzzle(
    day: int, year: int, f: PuzzleFunc, use_example: bool | None = None
) -> None:
    print(f"AOC {year} puzzle {day}")
    print("Getting inputs...", end=" ", flush=True)
    if use_example is None:
        use_example = bool(getenv("EXAMPLE"))
    with get_aoc_input(day, year, use_example=use_example) as inputs:
        print("done!")
        print("Running puzzle code...")
        print()
        start_time = perf_counter_ns()
        f(inputs)
        run_time = perf_counter_ns() - start_time
        print()
        print(f"All done ({run_time / 1000000:g} ms).")


def puzzle(f: PuzzleFunc) -> Puzzle:
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
    f.run_puzzle = partial(run_puzzle, day, year, f)  # type: ignore
    return cast(Puzzle, f)


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


def _input_file_path(puzzle: int, year: int, example: bool) -> Path:
    if example:
        file_name_template = EXAMPLE_FILE_TEMPLATE
    else:
        file_name_template = INPUT_FILE_TEMPLATE
    file_name = file_name_template.format(year=year, puzzle=puzzle)
    return INPUTS_DIR / file_name


def get_aoc_input(puzzle: int, year: int, use_example: bool = False) -> IO[str]:
    path = _input_file_path(puzzle, year, example=use_example)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        return path.open("r")
    except FileNotFoundError:
        if use_example:
            raise

    return _download_aoc_input(puzzle, year, path)


def _download_aoc_input(day: int, year: int, path: Path) -> IO[str]:
    # weirdly modularization, don't care about fixing the mess now. point for
    # now is only to contain code that imports `requests` so we don't need to
    # import it every time and we don't hard-fail if it's not available.
    import requests

    def get_aoc_url(url: str) -> requests.Response:
        _check_aoc_url(url)
        cookies = get_cookies()
        return requests.get(url, cookies=cookies)

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    response = get_aoc_url(url)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path.open("r")


def _check_aoc_url(url: str):
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme != "https" and parsed.netloc != "adventofcode.com":
        raise Exception(f"URL is not from https://adventofcode.com/: {url!r}")


def get_cookies() -> dict[str, str]:
    session = SESSION_PATH.read_text().strip()
    return {"session": session}


def path_for_puzzle(puzzle: int) -> tuple[Path, int, int]:
    path = Path(f"day{puzzle}.py")
    day, year = _get_day_and_year_from_path(path)
    return path, day, year


def _create_from_template(path: Path, day: int, year: int):
    template = TEMPLATE_PATH.read_text()
    path.write_text(template.format(DAY=day, YEAR=year))


def _edit_path(path: Path):
    editor = getenv("EDITOR")
    if not editor and getenv("TERM_PROGRAM") == "vscode":
        editor = "code"
    else:
        print(
            "You did not specify an editor and I cannot determine one to use. Currently"
            " only VS Code (`code`) is automatically detected. Otherwise the EDITOR"
            " environment variable is used.",
            file=sys.stderr,
        )
        sys.exit(1)
    from os import execvp

    execvp(editor, [editor, str(path.absolute())])


def _commit(day: int, year: int, path: Path):
    """
    Command to (kinda safely) commit changes to specific puzzle to git repo.

    Only works when following conventions (subject to change):

    1) all commits go to `main` branch

    2) commit message follows pattern "day 13" for first commit for day 13,
       "day 13 (more)" for any subsequent commit

    """
    from subprocess import run, PIPE

    files_for_puzzle: list[str] = [
        str(p)
        for p in [
            path,
            _input_file_path(day, year, example=False),
            _input_file_path(day, year, example=True),
        ]
        if p.is_file()
    ]
    if not files_for_puzzle:
        print("No files to commit.", file=sys.stderr)
        sys.exit(1)
    head = run(
        ["git", "symbolic-ref", "HEAD"],
        encoding="utf-8",
        check=True,
        stdout=PIPE,
    ).stdout.strip()
    if head != "refs/heads/main":
        print("HEAD is not main. I don't know how to commit.", file=sys.stderr)
        sys.exit(1)
    is_clean = run(["git", "diff-index", "--cached", "--quiet", "HEAD"]).returncode == 0
    if not is_clean:
        print("Repo has staged changes. I don't know how to commit.", file=sys.stderr)
        sys.exit(1)
    run(["git", "update-index", "--add", "--", *files_for_puzzle], check=True)
    is_clean = run(["git", "diff-index", "--cached", "--quiet", "HEAD"]).returncode == 0
    if is_clean:
        print("No files were changed.", file=sys.stderr)
        sys.exit(1)
    run(["git", "commit", "-m", f"day {day}"], check=True)


def _load_path(path: Path) -> ModuleType:
    # TODO: either just import the module by name, or explain why we don't do it
    from importlib.util import spec_from_file_location, module_from_spec

    name = path.with_suffix("").name
    spec = spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _run(day: int, year: int, path: Path, use_example: bool | None):
    if path.is_file():
        module = _load_path(path)
        for obj in module.__dict__.values():
            if isinstance(obj, Puzzle):
                callable = obj
                break
        else:
            print(
                f"{path} does not have any @puzzle-decorate function.", file=sys.stderr
            )
            sys.exit(1)
        callable.run_puzzle(use_example)
    else:
        _create_from_template(path, day, year)
        print(f"{path} created from template. Run command again to run puzzle.")


def _usage() -> NoReturn:
    print("usage:")
    print(f"  python {sys.argv[0]} <PUZZLE_DAY>", file=sys.stderr)
    print(f"  python {sys.argv[0]} <PUZZLE_DAY> edit", file=sys.stderr)
    print(f"  python {sys.argv[0]} <PUZZLE_DAY> edit-example", file=sys.stderr)
    print(f"  python {sys.argv[0]} <PUZZLE_DAY> run", file=sys.stderr)
    print(f"  python {sys.argv[0]} <PUZZLE_DAY> commit", file=sys.stderr)
    sys.exit(1)


def main():
    try:
        puzzle = int(sys.argv[1])
    except (ValueError, IndexError):
        _usage()

    if not 1 <= puzzle <= 25:
        print(f"{puzzle} is not a valid day for AOC", file=sys.stderr)
        sys.exit(1)

    path, day, year = path_for_puzzle(puzzle)

    try:
        action = sys.argv[2]
    except IndexError:
        action = "run"

    if action == "run":
        _run(day, year, path, use_example=None)
    elif action == "run-example":
        _run(day, year, path, use_example=True)
    elif action == "edit":
        if not path.exists():
            _create_from_template(path, day, year)
            print(f"{path} created from template. Opening in editor...")
        else:
            print(f"Opening {path} in editor...")
        _edit_path(path)
    elif action == "edit-example":
        if not path.exists():
            print(f"Note: {path} does not exist yet.")
        example_input_path = _input_file_path(day, year, example=True)
        _edit_path(example_input_path)
    elif action == "commit":
        _commit(day, year, path)
    else:
        _usage()


if __name__ == "__main__":
    main()
