import datetime as dt
import json
import os
from pathlib import Path
from subprocess import check_call, check_output, run

from protocli import Dispatcher

from . import _render
from .vars import (
    CFF_PATH,
    DOC_DIR,
    GITHUB_DIR,
    NOTES_PATH,
    ORCID_DIC_ENV,
    OSC_PATH,
    PYTHON_VERSION,
    README_PATH,
    TEMPLATE_BRANCH,
    TEST_DIR,
    Bump,
    bumped,
    conf,
)

DOCS_SCRIPT = Path(__file__).parent / "_docs.py"
ZENODO_BADGE = "[![DOI](https://zenodo.org/badge/doi/{doi}.svg)](https://doi.org/{doi})"


def lint(*, full: bool = False) -> None:
    """Format and lint with ruff: the package, or the whole repo with --full."""
    target = "." if full else conf.module_path
    _call("uv", "tool", "run", "ruff", "format", target)
    _call("uv", "tool", "run", "ruff", "check", "--fix", target)


def init(
    name: str,
    *,
    description: str = "",
    github_user: str = "",
    python_version: str = PYTHON_VERSION,
    actions: bool = False,
    os_compatibility: bool = False,
    single_file: bool = False,
    no_git: bool = False,
) -> None:
    """Create a project from the bundled template; the author comes from git config.

    Args:
        github_user: owner of the repo URL, `git config github.user` when omitted
        os_compatibility: with --actions, also test on windows and macos
    """
    root = Path(name)
    if root.exists():
        raise SystemExit(f"{root} already exists")
    ctx = _render.Context(
        name=name,
        description=description,
        author=_git_config("user.name"),
        email=_git_config("user.email"),
        github_user=github_user or _git_config("github.user"),
        python_version=python_version,
    )
    layout = _render.Layout(actions, os_compatibility, single_file)
    _render.write(_render.render(ctx, layout), root)
    os.chdir(root)
    check_call(["uv", "sync"])
    if not no_git:
        check_call(["git", "init", "-q", "-b", "main"])
        check_call(["git", "add", "-A"])
        check_call(["git", "commit", "-qm", "init"])
        check_call(["git", "branch", TEMPLATE_BRANCH])


def update_boilerplate(*, merge: bool = False) -> None:
    """Re-render .gitignore and the workflows on the template branch.

    A missing template branch starts from the current commit. --merge stages the
    merge here, uncommitted, for review.
    """
    _require_clean()
    rendered = _render.render(_project_context(), _project_layout())
    files = {k: v for k, v in rendered.items() if k.startswith(_render.MANAGED)}
    branch = _get_branch()
    if run(
        ["git", "show-ref", "-q", "--verify", f"refs/heads/{TEMPLATE_BRANCH}"]
    ).returncode:
        check_call(["git", "branch", TEMPLATE_BRANCH])
    check_call(["git", "checkout", "-q", TEMPLATE_BRANCH])
    check_call(["git", "rm", "-q", "--ignore-unmatch", "--", *_render.RETIRED])
    _render.write(files, Path("."))
    check_call(["git", "add", "--", *files])
    if run(["git", "diff", "--cached", "--quiet"]).returncode:
        check_call(["git", "commit", "-qm", "update-boilerplate"])
    check_call(["git", "checkout", "-q", branch])
    if merge:
        _call("git", "merge", "--no-ff", "--no-commit", TEMPLATE_BRANCH)


def test(*, v: bool = False, no_cov: bool = False) -> None:
    """Lint, then pytest with doctests; coverage lands in coverage/ (HTML, markdown)."""
    lint()
    comm = [
        "uv",
        "run",
        "--with",
        "pytest",
        "--with",
        "pytest-cov",
        "python",
        "-m",
        "pytest",
        conf.module_path,
        "--doctest-modules",
    ]
    if TEST_DIR.is_dir():
        comm.append(TEST_DIR.as_posix())
    if not no_cov:
        comm += [
            f"--cov={conf.name}",
            "--cov-report=html:coverage/html",
            "--cov-report=term-missing",
        ]
    if v:
        comm.append("-s")
    failed = run(comm).returncode
    if not no_cov and Path(".coverage").exists():
        report = run(
            [
                "uv",
                "run",
                "--with",
                "coverage",
                "python",
                "-m",
                "coverage",
                "report",
                "--format=markdown",
            ],
            capture_output=True,
            text=True,
        )
        cov_dir = Path("coverage")
        cov_dir.mkdir(exist_ok=True)
        (cov_dir / "report.md").write_text(report.stdout)
    if failed:
        raise SystemExit(1)


def build_docs() -> None:
    """Generate docs/api.md from docstrings, in the project's own environment."""
    out = (DOC_DIR / "api.md").as_posix()
    check_call(["uv", "run", "python", "-I", DOCS_SCRIPT.as_posix(), conf.name, out])


def tag(notes: str, bump: Bump) -> None:
    """Release: one commit (version, notes, CFF), an annotated tag, one atomic push.

    Args:
        notes: release notes, the tag message and the GitHub release body
    """
    branch = _get_branch()
    if branch != "main":
        raise SystemExit(f"only main can be tagged, not {branch}")
    version = bumped(conf.version, bump)
    name = f"v{version}"
    if check_output(["git", "tag", "--list", name], text=True).strip():
        raise SystemExit(f"{name} is already tagged")
    paths = [conf.version_file]
    if DOC_DIR.exists():
        paths.append(NOTES_PATH)
    if CFF_PATH.exists():
        paths.append(CFF_PATH)
    _require_clean(*paths)

    conf.write_version(version)
    if NOTES_PATH in paths:
        _prepend_notes(name, notes)
    if CFF_PATH in paths:
        _mod_cff({"version": version, "date-released": dt.date.today().isoformat()})
    staged = [p.as_posix() for p in paths]
    check_call(["git", "add", "--", *staged])
    check_call(["git", "commit", "-qm", f"release {name}", "-m", notes, "--", *staged])
    check_call(["git", "tag", "-a", name, "-m", notes])
    check_call(["git", "push", "--atomic", "origin", branch, name])


def init_cff(
    *,
    message: str = "If you use this software, please cite it as below.",
    license: str = "MIT",
) -> None:
    project = conf.project_conf
    url = project["urls"]["Homepage"]
    orcids = json.loads(os.environ.get(ORCID_DIC_ENV, "{}"))
    lines = [
        "cff-version: 1.2.0",
        f"message: {_yaml(message)}",
        f"url: {_yaml(url)}",
        "authors:",
    ]
    for author in project["authors"]:
        *given, family = author["name"].split()
        lines += [
            f"- family-names: {_yaml(family)}",
            f"  given-names: {_yaml(' '.join(given))}",
        ]
        if orcid := orcids.get(author["name"]):
            lines.append(f"  orcid: {_yaml(orcid)}")
    lines += [
        f"title: {_yaml('/'.join(url.split('/')[-2:]))}",
        f"license: {_yaml(license)}",
        f"keywords: {_yaml(project.get('keywords', []))}",
        "type: software",
    ]
    CFF_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


init_cff.__doc__ = (
    f"Write CITATION.cff from pyproject.toml; ${ORCID_DIC_ENV} maps authors to ORCIDs."
)


def add_zenodo_concept_doi(doi: int) -> None:
    """Put the Zenodo concept DOI badge in the README and the DOI in CITATION.cff."""
    full_doi = f"10.5281/zenodo.{doi}"
    badge_start = ZENODO_BADGE.split("{")[0]
    readme = README_PATH.read_text(encoding="utf-8").split("\n")
    lines = [li for li in readme if not li.startswith(badge_start)]
    lines.insert(2, ZENODO_BADGE.format(doi=full_doi))
    README_PATH.write_text("\n".join(lines), encoding="utf-8")
    if CFF_PATH.exists():
        _mod_cff({"doi": full_doi})


def _project_context() -> _render.Context:
    project = conf.project_conf
    author = project["authors"][0]
    return _render.Context(
        name=project["name"],
        description=project.get("description", ""),
        author=author["name"],
        email=author["email"],
        github_user=project["urls"]["Homepage"].split("/")[-2],
        python_version=project["requires-python"].removeprefix(">="),
    )


def _project_layout() -> _render.Layout:
    return _render.Layout(
        actions=GITHUB_DIR.exists(),
        os_compatibility=OSC_PATH.exists(),
        single_file=conf.module_path.endswith(".py"),
    )


def _get_branch() -> str:
    return check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()


def _git_config(key: str) -> str:
    value = run(["git", "config", key], capture_output=True, text=True).stdout.strip()
    if not value:
        raise SystemExit(f"git config {key} is not set")
    return value


def _require_clean(*paths: Path) -> None:
    comm = [
        "git",
        "status",
        "--porcelain",
        "--untracked-files=no",
        "--",
        *map(str, paths),
    ]
    dirty = check_output(comm, text=True)
    if dirty:
        raise SystemExit(f"commit or stash these first:\n{dirty}")


def _call(*args: str) -> None:
    if run(args).returncode:
        raise SystemExit(1)


def _prepend_notes(name: str, notes: str) -> None:
    entry = f"## {name}\n\n{notes}\n"
    existing = NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""
    NOTES_PATH.write_text(
        f"{entry}\n---\n\n{existing}" if existing else entry, encoding="utf-8"
    )


def _yaml(value: object) -> str:
    """JSON scalars and lists are valid YAML, quoted where YAML would misread them."""
    return json.dumps(value, ensure_ascii=False)


def _mod_cff(values: dict[str, str]) -> None:
    """Set top-level CITATION.cff keys in place, leaving every other line as it is."""
    lines = CFF_PATH.read_text(encoding="utf-8").splitlines()
    for key, value in values.items():
        line = f"{key}: {_yaml(value)}"
        at = next((i for i, li in enumerate(lines) if li.startswith(f"{key}:")), None)
        if at is None:
            lines.append(line)
        else:
            lines[at] = line
    CFF_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


cli = Dispatcher(
    "branb",
    {
        "lint": lint,
        "init": init,
        "update-boilerplate": update_boilerplate,
        "test": test,
        "build-docs": build_docs,
        "tag": tag,
        "init-cff": init_cff,
        "add-zenodo-concept-doi": add_zenodo_concept_doi,
    },
).run
