## v7.0.0

- **Breaking:** `update-boilerplate` re-renders and merges only `.gitignore` and the GitHub workflows; every other file is the project's own after `init` and is no longer touched.
- **Breaking:** `--merge` now stages a `--no-ff` merge without committing it, leaving the commit for review, instead of committing automatically.
- `update-boilerplate` creates the template branch from the current commit when it's missing instead of failing.
- `init` runs `uv sync` before the first commit, so `uv.lock` lands in it instead of a separate commit.
- Fixed a crash in `update-boilerplate` when `pyproject.toml` has no project description.
- Bumped `actions/checkout` to v7 and `astral-sh/setup-uv` to v10.3.0 in the repo's and the template's workflows, so new and updated projects pick up the same versions.

---

## v6.0.0

- **Breaking:** `branb init` now takes the project name as a required argument and renders the template bundled in `branthebuilder/template/` instead of prompting via cookiecutter; author/email/github-user are read from `git config` instead of interactive input.
- **Breaking:** CLI flags renamed or inverted: `test --cov` is now `test --no-cov`, `init --git` is now `init --no-git`, and the message arguments of `tag` and `init-cff` were renamed.
- **Breaking:** branthebuilder's only runtime dependency is now `protocli`; `cookiecutter`, `typer` and `pyyaml` are gone, ruff runs via `uv tool run`, and pytest is a dev-only dependency.
- `branb tag` now makes a single `release vX.Y.Z` commit (version, release notes, CITATION.cff), refuses to run if those files have other uncommitted changes, and pushes the branch and tag atomically.
- Pushing a `vX.Y.Z` tag now drives the release via a new `release.yml` workflow: it waits on the test gate, then builds, publishes to PyPI, and creates the GitHub release with the tag notes and built dists attached; the old publish-on-GitHub-release workflow is removed.
- `branb update-boilerplate` re-renders the template directly onto the `template` branch and removes files the template no longer produces.
- `branb build-docs` now generates API docs by running in the project's own interpreter instead of importing the project into branb's environment.
- README rewritten to document the bundled template, the tag-driven release flow, and updated usage examples.</notes>

---

## v5.1.0

test directory if present

---

## v5.0.1

workflows

---

## v5.0.0

large cleanup
