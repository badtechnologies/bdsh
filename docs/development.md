---
title: Development
nav_order: 8
---

# Development

bdsh is a Python project under `src/bdsh`. It supports Python 3.10 and newer.

## Set up and test

From the repository root, install the project in editable mode with its test dependency and run the test suite:

```sh
python3 -m pip install -e ".[test]"
python3 -m pytest
```

The GitHub Actions test workflow runs the same suite on Python 3.12.

## Project areas

- `src/bdsh/command/` implements shell commands, including bpm and BOSS.
- `src/bdsh/service/` implements user login, networking, and local RPC services.
- `src/bdsh/install/` initializes the shell data directories and user database.
- `src/bdsh/io/` provides terminal input and output.
- `src/bdsh/util/` contains executable loading, version selection, and JSON validation.
- `tests/` contains the pytest suite.
- `kernel/` contains the Buildroot external tree and image-building scripts; see the [kernel guide](kernel/index.md).

## Documentation site

The documentation is a Jekyll site in `docs/`, using the Just the Docs theme. Its GitHub Pages workflow builds the contents of that directory on pushes to `main`.
