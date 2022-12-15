# aoc2022
Just an archive of [my](https://github.com/sorcio) solutions for [Advent of
Code 2022](https://adventofcode.com/2022) puzzles.

## Disclaimer

The purpose of this repository is just archival, or sharing with friends. While
all the content is available to the public under a free software license, it's
probably not useful to you.

The solutions are usually tested to work, but they are not a good reference.
I solve Advent of Code puzzles for fun. To make it interesting to myself,
I often enforce arbitrary restrictions, or experiment with some unusual
techinque, or try to come up with the quickest or weirdest solution. Most of
these choices are not documented. Additionally, I rarely spend any time
polishing the code after I found a working solution.

## aoc.py

The code includes a script to run Python puzzles and downloading inputs from
the AOC website. While not very polished, it can be useful to others.

> Consider using a well-maintained package like
> [advent-of-code-data](https://pypi.org/project/advent-of-code-data/) instead
> of this.

The runner follows some very narrow conventions:

- all code is contained in a directory called `aocYEAR` (e.g. `aoc2022`), and
  the solution for a given day is called `dayN.py` (e.g. `aoc2022/day14.py`).

- each solution file contains a function decorated with `@puzzle` which takes a
  text file-like object as its only argument:

  ```python
  from aoc import puzzle
  from typing import IO

  @puzzle
  def day14(input: IO[str]) -> None:
    ...
  ```

- for the `commit` command to work, all code must be included in a git repo,
  and commits go to the `main` branch.

- in order to download inputs, a file called `.sessionid` must be present in
  the current directory, with the content of the sessionid cookie for
  https://adventofcode.com

- all inputs are saved as text files like `inputs/input_2022_14.txt` (for
  `day14.py`). The script will automatically attempt to download this file if
  it does not exist. You can also manually populate a file called like
  `inputs/input_2022_14.example.txt`, which will be used for the `run-example`
  command.

### Usage

Call the script with the number of the day and optionally a command (default is
`run`).

**python aoc.py** *DAY* [*COMMAND*]

* `run`: (default command) download the input file if necessary, then run the
  first `@puzzle` function defined in the `day<DAY>.py` file. If the file does
  not exist, an empty one will be generated from a template and nothing else
  will be done.

* `run-example`: similar to run, but instead of downloading the input, use the
  example input file for that day (must be manually populated, see above).

* `edit`: open the `day<DAY>.py` file in an editor. If run from within VS Code,
  attempt to open in the same editor window. Otherwise use `$EDITOR`.

* `edit-example`: open the `inputs/input_<YEAR>_<DAY>.example.txt` file (the
   example input file) in an editor.

* `commit`: create a new git commit on the main branch with all the available
  files for the given day (the Python file, the input file, the example input
  file).

## License

You can use this software under the terms specified in the included
[LICENSE](LICENSE) file, with the exception of the content of the `inputs/`
directory which is sourced from the [Advent of Code](https://adventofcode.com/)
website which specifies different terms.
