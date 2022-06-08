import toml

PREFIX = "sudoku-"
PACKAGE_TEMPLATE = toml.loads(
    """[tool.poetry]
name = "cell11"
version = "1.0.0"
description = ""
authors = []

[tool.poetry.dependencies]
python = "^3.6"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""
)
PROBLEM_TEMPLATE = toml.loads(
    """[tool.poetry]
name = "sudoku-problem"
version = "1.0.0"
description = ""
authors = []

[[tool.poetry.source]]
name = 'devpi'
url = 'http://localhost:3141/poetry/sudoku/+simple/'
default = true

[tool.poetry.dependencies]
python = "^3.6"

[tool.poetry.dev-dependencies]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""
)
