from pathlib import Path
from subprocess import check_call, check_output, run

import pytest

import branthebuilder.main as ns
from branthebuilder import _render
from branthebuilder.vars import (
    CFF_PATH,
    NOTES_PATH,
    README_PATH,
    TEMPLATE_BRANCH,
    conf,
)


def _git(*args: str) -> str:
    return check_output(["git", *args], text=True).strip()


@pytest.mark.parametrize("single_file,actions", [(False, True), (True, False)])
def test_integration(tmp_path, monkeypatch, single_file, actions):
    monkeypatch.chdir(tmp_path)
    check_call(["git", "init", "-q", "--bare", "-b", "main", "remote"])
    ns.init(
        "testproject", github_user="someone", actions=actions, single_file=single_file
    )
    if single_file:
        with Path("testproject.py").open("a") as f:
            f.write(DOCTESTED_FUN)
        _git("commit", "-qam", "dtfun")
    _git("remote", "add", "origin", "../remote")
    _git("push", "-q", "--set-upstream", "origin", "main")

    ns.lint()
    ns.test(v=True)
    ns.build_docs()
    if single_file:
        assert "## `fing(x)`" in Path("docs", "api.md").read_text()

    ns.add_zenodo_concept_doi(1238979)
    ns.init_cff()
    ns.add_zenodo_concept_doi(7658979)
    assert "1238979" not in README_PATH.read_text()
    assert "7658979" in README_PATH.read_text()
    assert "zenodo.7658979" in CFF_PATH.read_text()
    _git("add", "-A")
    _git("commit", "-qm", "citation")

    original = conf.version_file.read_text()
    conf.version_file.write_text(original + "# unrelated edit\n")
    with pytest.raises(SystemExit):
        ns.tag("refused", "minor")
    assert conf.version_file.read_text().endswith("# unrelated edit\n")
    conf.version_file.write_text(original)

    for bump in ("minor", "major", "bug"):
        ns.tag(f"- {bump} release", bump)
    releases = ["v1.0.1", "v1.0.0", "v0.1.0"]
    assert _git("log", "--format=%s", "-3").split("\n") == [
        f"release {r}" for r in releases
    ]
    assert _git("--git-dir=../remote", "tag").split() == sorted(releases)
    assert NOTES_PATH.read_text().startswith("## v1.0.1\n\n- bug release")
    assert 'version: "1.0.1"' in CFF_PATH.read_text()
    check_call(["uv", "build"])

    retired = Path(_render.RETIRED[-1])
    _git("checkout", "-q", TEMPLATE_BRANCH)
    retired.write_text("from an earlier template")
    _git("add", retired.as_posix())
    _git("commit", "-qm", "earlier template")
    _git("checkout", "-q", "main")
    _git("merge", "-q", "--no-edit", TEMPLATE_BRANCH)
    ns.update_boilerplate(merge=True)
    assert not retired.exists()
    _git("commit", "-q", "--no-edit")

    _git("branch", "-D", TEMPLATE_BRANCH)
    gitignore = Path(".gitignore")
    rendered = gitignore.read_text()
    gitignore.write_text("stale\n")
    _git("commit", "-qam", "stale gitignore")
    wip = README_PATH.read_text() + "work in progress\n"
    README_PATH.write_text(wip)
    ns.update_boilerplate(merge=True)
    assert gitignore.read_text() == rendered
    assert README_PATH.read_text() == wip


def test_link(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    package = Path("sibling", "src", "sibling")
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    ns.init("linked", github_user="someone", no_git=True)
    probe = ["uv", "run", "python", "-c", "import sibling"]
    ns.link("../sibling")
    check_call(probe)
    ns.link()
    assert run(probe, capture_output=True).returncode


DOCTESTED_FUN = '''
def fing(x):
    """add two
    >>> fing(3)
    5
    """
    return x + 2
'''
