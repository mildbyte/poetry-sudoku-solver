from typing import List

import toml


def parse_solution(lockfile: str) -> str:
    with open(lockfile, "r") as f:
        data = toml.load(f)

    cell_values = {
        (int(p["name"][-2]), int(p["name"][-1])): int(p["version"][0])
        for p in data["package"]
    }

    lines: List[str] = []
    for row in range(1, 10):
        if row in (4, 7):
            lines.append("-------|-------|-------")
        line = " "
        for col in range(1, 10):
            if col in (4, 7):
                line += "| "
            line += f"{cell_values[row, col]} "
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    grid = parse_solution("./problem/poetry.lock")
    print(grid)
