import os
from pathlib import Path
from typing import Any, Dict, Tuple

import toml

from poetry_sudoku_solver.templates import PREFIX, PROBLEM_TEMPLATE


def string_to_problem(pstr: str) -> Dict[Tuple[int, int], int]:
    result: Dict[Tuple[int, int], int] = {}
    rows = [
        r.strip()
        for r in pstr.replace(" ", "").replace("|", "").replace("-", "").splitlines()
        if r.strip()
    ]
    for row, rval in enumerate(rows):
        for col, cval in enumerate(rval):
            if str.isdigit(cval):
                result[(row + 1, col + 1)] = int(cval)

    return result


def generate_problem(cells: Dict[Tuple[int, int], int]) -> Dict[str, Any]:
    package = PROBLEM_TEMPLATE.copy()
    for row in range(1, 10):
        for col in range(1, 10):
            version = cells.get((row, col))
            package["tool"]["poetry"]["dependencies"][f"{PREFIX}cell{row}{col}"] = (
                f"{version}.0.0" if version else "*"
            )

    return package


def generate_and_save_problem(
    cells: Dict[Tuple[int, int], int], problem_dir: str
) -> None:
    package_json = generate_problem(cells)
    Path(problem_dir).mkdir(exist_ok=True, parents=True)
    with open(os.path.join(problem_dir, "pyproject.toml"), "w") as f:
        toml.dump(package_json, f)
    with open(
        os.path.join(problem_dir, "sudoku_problem.py"),
        "w",
    ):
        pass
