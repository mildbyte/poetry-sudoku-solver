# poetry-sudoku-solver

Sudoku solver that uses Poetry's dependency resolver

## How it works

This package is supposed to be used with [devpi](https://github.com/devpi/devpi), a local PyPI server.

First, it generates 9 x 9 = 81 Python "packages", each of which represents
a Sudoku cell. Each package has 9 versions, corresponding to cell values.
Finally, each package also has dependencies on other "cell" packages, with
version constraints encoding which values those "cells" can have.

For example, version 3.0.0 of the `sudoku-cell25` package represents an
assertion that the cell at row 2, column 5 of the board has the number 3
in it. The `pyproject.toml` for this package has a list of all "cell" 
packages  in the same row, column or a 3x3 square as this cell:

```toml
[tool.poetry.dependencies]
python = "^3.6"
sudoku-cell14 = "!= 3.0.0"
sudoku-cell15 = "!= 3.0.0"
sudoku-cell16 = "!= 3.0.0"
sudoku-cell21 = "!= 3.0.0"
sudoku-cell22 = "!= 3.0.0"
sudoku-cell23 = "!= 3.0.0"
sudoku-cell24 = "!= 3.0.0"
sudoku-cell26 = "!= 3.0.0"
sudoku-cell27 = "!= 3.0.0"
sudoku-cell28 = "!= 3.0.0"
sudoku-cell29 = "!= 3.0.0"
sudoku-cell34 = "!= 3.0.0"
sudoku-cell35 = "!= 3.0.0"
sudoku-cell36 = "!= 3.0.0"
sudoku-cell45 = "!= 3.0.0"
sudoku-cell55 = "!= 3.0.0"
sudoku-cell65 = "!= 3.0.0"
sudoku-cell75 = "!= 3.0.0"
sudoku-cell85 = "!= 3.0.0"
sudoku-cell95 = "!= 3.0.0"
```

Then, it uploads these packages to devpi. Theoretically, one could upload
them to PyPI (these rules are only ever uploaded once, not every time we
need to solve a board), but that feels kinda abusive.

Now, we can represent an unsolved Sudoku board as another Poetry package:

```
[tool.poetry.dependencies]
python = "^3.6"
sudoku-cell11 = "*"
sudoku-cell12 = "2.0.0"
sudoku-cell13 = "*"
sudoku-cell14 = "8.0.0"
sudoku-cell15 = "*"
sudoku-cell16 = "9.0.0"
sudoku-cell17 = "*"
sudoku-cell18 = "*"
sudoku-cell19 = "*"
sudoku-cell21 = "3.0.0"
sudoku-cell22 = "7.0.0"
sudoku-cell23 = "*"
sudoku-cell24 = "6.0.0"
...
```

This `pyproject.toml` depends on all 81 "cell" packages, pinning known
cells to their values. In order to generate a lockfile for this package,
Poetry has to find a version (value) for each of the 81 packages (cells)
in such a way that they don't conflict with each other. Since we encoded
the rules of Sudoku as inter-package dependencies, the lockfile will
contain a solution to this Sudoku board.

## Usage

Install [Poetry](https://python-poetry.org/docs/#installation).

### Installing the package and the prerequisites

```bash
poetry install
```

All the commands after this are supposed to be run in the package's virtual
environment. You can enter it by running:

```bash
poetry shell
```

### Setting up devpi

```bash
devpi-init
devpi-server
```

Create a devpi user and add devpi to Poetry as a repository:

```bash
devpi user -c poetry password=poetry
devpi login poetry --password=poetry
poetry config repositories.devpi http://localhost:3141/poetry/sudoku
```

(there's no need to add the devpi credentials to Poetry, since the next 
"publish" command embeds the password in the Poetry invocation).

### Building and publishing the "constraint" packages

You only need to do this step once (instead of to solve every Sudoku problem)

```bash
poetry-sudoku-solver generate-packages
poetry-sudoku-solver publish-packages
```

The second step will take a few minutes, as it will publish 9 x 9 x 9 = 729
versions of packages to the local devpi instance.

### Generate a "problem" package and solve it

Visit https://qqwing.com/generate.html to generate a Sudoku puzzle. Paste it
into `./problem.txt`.

Generate the package with the representation of the problem:

```bash
poetry-sudoku-solver generate-problem-package ./problem.txt
```

Run Poetry's dependency resolver. This will pin each package to a specific
version that represents the value of each Sudoku cell.

```bash
cd output/problem && poetry update --lock
```

Parse the lockfile and output the Sudoku solution:

```bash
poetry-sudoku-solver parse-solution ./poetry.lock
```

You can also run all three of these at once:

```bash
poetry-sudoku-solver solve ./problem.txt
```
