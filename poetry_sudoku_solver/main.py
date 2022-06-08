import os
import subprocess

import click

from poetry_sudoku_solver.packages import build_package_dir
from poetry_sudoku_solver.packages import publish_packages as publish
from poetry_sudoku_solver.problem import (generate_and_save_problem,
                                          string_to_problem)
from poetry_sudoku_solver.solution import parse_solution as parse_solution_


@click.command("generate-packages")
@click.argument(
    "directory",
    default="./output/cells",
    type=click.Path(dir_okay=True, file_okay=False, exists=False),
)
def generate_packages(directory):
    """Generate constraint packages.

    These packages represent constraints on a valid Sudoku board.
    """
    build_package_dir(directory)


@click.command("publish-packages")
@click.argument(
    "directory",
    default="./output/cells",
    type=click.Path(dir_okay=True, file_okay=False, exists=False),
)
def publish_packages(directory):
    """Upload the constraint packages to devpi."""
    publish(directory)


@click.command("generate-problem-package")
@click.argument("problem", type=click.File("r"), default="./problem.txt")
@click.argument(
    "directory",
    default="./output/problem",
    type=click.Path(dir_okay=True, file_okay=False, exists=False),
)
def generate_problem_package(problem, directory):
    """Generate a "problem" package.

    This package represents the unsolved Sudoku board.

    The input file must be a textual representation of the board in the same
    format as https://qqwing.com/generate.html
    """
    cells = string_to_problem(problem.read())
    generate_and_save_problem(cells, directory)


@click.command("parse-solution")
@click.argument(
    "lockfile",
    default="./output/problem/poetry.lock",
    type=click.Path(dir_okay=False, file_okay=True, exists=True),
)
@click.argument("output", type=click.File("w"), default="-")
def parse_solution(lockfile, output):
    """Parse a generated Poetry lockfile.

    After running cd output/problem && poetry update --lock, the lockfile
    will contain the solution to the Sudoku problem. This command parses it
    into a textual representation of the board."""
    solution = parse_solution_(lockfile)
    output.write(solution)


@click.command("solve")
@click.argument("problem", type=click.File("r"), default="./problem.txt")
@click.argument("output", type=click.File("w"), default="-")
@click.option("-w", "--workdir", default="./output")
def solve(problem, output, workdir):
    """Parse and solve a Sudoku problem with Poetry.

    This runs generate-problem-package, the Poetry lockfile resolver and
    parses the solution. You still need to have previously uploaded the constraint packages to devpi."""
    package_dir = os.path.join(workdir, "problem")
    cells = string_to_problem(problem.read())
    generate_and_save_problem(cells, package_dir)

    with open(os.path.join(workdir, "poetry.log"), "w") as f:
        subprocess.check_call(
            ["poetry", "update", "--lock", "-vvv"], cwd=package_dir, stdout=f
        )

    solution = parse_solution_(os.path.join(package_dir, "poetry.lock"))
    output.write(solution)


@click.group(name="solver")
def solver():
    pass


solver.add_command(generate_packages)
solver.add_command(publish_packages)
solver.add_command(generate_problem_package)
solver.add_command(parse_solution)
solver.add_command(solve)


if __name__ == "__main__":
    solver()
