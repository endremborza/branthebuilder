# branthebuilder

[![pypi](https://img.shields.io/pypi/v/branthebuilder.svg)](https://pypi.org/project/branthebuilder/)

Utility CLI for creating, documenting, and testing Python packages. Uses a [cookiecutter template](https://github.com/endremborza/python-boilerplate-v2).

## Philosophy

This project embodies a **self-contained, low-dependency** approach to Python library development. Projects built with it follow the same principles.

### Core principles

- **No external services** — no codecov, no readthedocs, no hosted CI artifacts. Everything lives in the repo.
- **Docs in the repo** — documentation is generated into `docs/` as HTML and Markdown, readable by both humans and AI tools without a browser.
- **Coverage in the repo** — test coverage reports are generated locally into `coverage/`, in HTML and Markdown formats, committed alongside the code.
- **Minimal dependencies** — avoid heavy frameworks unless the value is clear and lasting. Prefer stdlib, then small focused libraries with few transitive deps.
- **Modern Python tooling** — `uv` for dependency management, `ruff` for formatting and linting, `hatchling` for builds, `pyproject.toml` as the single config source.
- **AI-friendly** — Markdown output for docs and coverage means both humans and LLMs can read and reason about the project state without fetching external URLs.

### Doc generation

API docs are generated from docstrings into `docs/api.md` using Python's `inspect` module. No external tools required. Release notes live in `docs/release_notes.md`, with the newest release always on top.

```
branb build-docs   # generates docs/api.md from docstrings
branb tag "msg" minor  # prepends entry to docs/release_notes.md
```

### Coverage

`pytest-cov` + `coverage` built-in Markdown reporter (coverage ≥ 7.2):

```
branb test         # runs lint + pytest, writes coverage/ with HTML and report.md
```

Coverage output is committed to the repo so it is always readable in-browser on GitHub and by any LLM with repo access.

## Usage

```bash
# create a new project from the cookiecutter template
branb init

# lint (ruff format + check)
branb lint

# run tests with coverage
branb test

# build docs
branb build-docs

# tag a release and push
branb tag "release message" minor
```

## Installation

```bash
uv tool install branthebuilder
```

thanks to typer, can install shell completion after

## License

MIT

