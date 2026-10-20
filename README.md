# branthebuilder

[![pypi](https://img.shields.io/pypi/v/branthebuilder.svg)](https://pypi.org/project/branthebuilder/)

Utility CLI for creating, documenting, testing and releasing Python packages. Projects are rendered from the template bundled in `branthebuilder/template/`.

## Philosophy

This project embodies a **self-contained, low-dependency** approach to Python library development. Projects built with it follow the same principles.

### Core principles

- **No external services** — no codecov, no readthedocs, no hosted CI artifacts. Everything lives in the repo.
- **Docs in the repo** — documentation is generated into `docs/` as HTML and Markdown, readable by both humans and AI tools without a browser.
- **Coverage in the repo** — test coverage reports are generated locally into `coverage/`, in HTML and Markdown formats, committed alongside the code.
- **Minimal dependencies** — avoid heavy frameworks unless the value is clear and lasting. Prefer stdlib, then small focused libraries with few transitive deps. branb itself depends on `protocli` alone; ruff, pytest and coverage run through `uv` on demand.
- **Modern Python tooling** — `uv` for dependency management, `ruff` for formatting and linting, `hatchling` for builds, `pyproject.toml` as the single config source.
- **AI-friendly** — Markdown output for docs and coverage means both humans and LLMs can read and reason about the project state without fetching external URLs.

### Doc generation

API docs are generated from docstrings into `docs/api.md` using Python's `inspect` module, run with the project's own interpreter (`uv run`) so the package imports in its own environment. No external tools required. Release notes live in `docs/release_notes.md`, with the newest release always on top.

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

### Releasing

A release is a pushed tag, never a click on GitHub. `branb tag "notes" minor` makes one `release vX.Y.Z` commit holding the bumped `__version__`, the notes prepended to `docs/release_notes.md` (when `docs/` exists) and the new version and date in `CITATION.cff` (when it exists). It tags that commit `vX.Y.Z` with the notes as the message and pushes the branch and the tag atomically. It refuses to start while any of those files has other uncommitted changes, so a release never sweeps in unrelated work.

The tag push runs `.github/workflows/release.yml`: once the workflow its `gate` job calls passes, it builds, publishes to PyPI with the `PYPI_TOKEN` secret and creates the GitHub release from the tag message, with the built dists attached. The gate is `test.yml`; pointing it at `compatibility_test.yml` also requires the OS matrix. A push without a tag only runs the tests.

### Template

`branb init <name>` renders `branthebuilder/template/`, replacing each `{{field}}` of `_render.Context` in paths and contents, with the author taken from `git config user.name`/`user.email` and the GitHub owner from `--github-user` or `git config github.user`. `--actions` adds the workflows, `--os-compatibility` the OS matrix, `--single-file` a module instead of a package. The first commit holds everything, including `uv.lock`, and the template branch (`vars.TEMPLATE_BRANCH`) points at it.

After `init` the project owns every file except those matching `_render.MANAGED` (`.gitignore` and the workflows). `branb update-boilerplate` re-renders those with the project's current values and layout onto the template branch and commits them there, so a three-way merge keeps the project's own edits to them. `--merge` stages that merge on the current branch without committing it, for review. A missing template branch starts from the current commit, so its first merge overwrites the managed files and the review is where project-specific lines get restored. A file the template no longer produces is listed in `_render.RETIRED`, which removes it from the template branch, so the merge deletes it from the project unless the project changed it.

## Usage

```bash
# create a new project from the bundled template
branb init myproject --actions

# lint (ruff format + check)
branb lint

# run tests with coverage
branb test

# build docs
branb build-docs

# tag and push; CI publishes the release once the tests pass
branb tag "release message" minor

# stage template changes to .gitignore and the workflows, then review and commit
branb update-boilerplate --merge

# citation metadata
branb init-cff
branb add-zenodo-concept-doi 1234567
```

## Installation

```bash
uv tool install branthebuilder
```

`branb --complete <args…>` prints completion candidates for shell integration (protocli).

## License

MIT

