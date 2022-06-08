import contextlib
import os
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple

import toml
from tqdm.contrib.concurrent import thread_map

from poetry_sudoku_solver.templates import PACKAGE_TEMPLATE, PREFIX


def get_conflicting_cells(cell_row: int, cell_col: int) -> List[Tuple[int, int]]:
    result: List[Tuple[int, int]] = []

    cell_square_start_row = (cell_row - 1) // 3 + 1
    cell_square_start_col = (cell_col - 1) // 3 + 1

    for row in range(1, 10):
        for col in range(1, 10):
            if row == cell_row and col == cell_col:
                continue

            square_start_row = (row - 1) // 3 + 1
            square_start_col = (col - 1) // 3 + 1

            if (
                # Same column
                (col == cell_col and row != cell_row)
                # Same row
                or (row == cell_row and col != cell_col)
                # Same square
                or (
                    cell_square_start_col == square_start_col
                    and cell_square_start_row == square_start_row
                )
            ):
                result.append((row, col))

    return result


def build_pyproject_file(
    cell_row: int, cell_col: int, cell_value: int
) -> Dict[str, Any]:
    cells = get_conflicting_cells(cell_row, cell_col)

    package_json = deepcopy(PACKAGE_TEMPLATE)
    package_json["tool"]["poetry"]["name"] = f"{PREFIX}cell{cell_row}{cell_col}"
    package_json["tool"]["poetry"]["version"] = f"{cell_value}.0.0"

    package_json["tool"]["poetry"]["dependencies"].update(
        {f"{PREFIX}cell{r}{c}": f"!= {cell_value}.0.0" for (r, c) in cells}
    )
    return package_json


def build_package_dir(basedir: str) -> None:
    for row in range(1, 10):
        for col in range(1, 10):
            for val in range(1, 10):
                version_dir = os.path.join(basedir, f"{PREFIX}cell{row}{col}-{val}.0.0")
                Path(version_dir).mkdir(exist_ok=True, parents=True)
                with open(os.path.join(version_dir, "pyproject.toml"), "w") as f:
                    toml.dump(build_pyproject_file(row, col, val), f)
                with open(
                    os.path.join(
                        version_dir, f"{PREFIX}cell{row}{col}.py".replace("-", "_")
                    ),
                    "w",
                ) as f:
                    pass


def publish_packages(basedir: str) -> None:
    # Publish all versions
    all_versions = [(row, col) for row in range(1, 10) for col in range(1, 10)]

    # Purge the index (ignore if it doesn't exist)
    with contextlib.suppress(subprocess.CalledProcessError):
        subprocess.check_call(["devpi", "index", "--delete", "-y", "poetry/sudoku"])

    # ... and recreate it
    subprocess.check_call(["devpi", "index", "-c", "poetry/sudoku"])

    def _work(v: Tuple[int, int]) -> None:
        row, col = v
        for val in range(1, 10):
            cwd = os.path.join(basedir, f"{PREFIX}cell{row}{col}-{val}.0.0")
            subprocess.check_call(
                ["poetry", "build", "-f", "wheel"],
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.check_call(
                [
                    "poetry",
                    "publish",
                    "-r",
                    "devpi",
                    "-u",
                    "poetry",
                    "-p",
                    "poetry",
                ],
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    list(thread_map(_work, all_versions, max_workers=16))
