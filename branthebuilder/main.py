import os
from pathlib import Path
from shutil import rmtree
from subprocess import check_call, check_output
from warnings import warn

import typer
from cookiecutter.main import cookiecutter

from .nb_scripts import get_nb_scripts, get_notebooks, nb_dir
from .vars import cc_repo, conf, current_release_path, docdir

app = typer.Typer()


class SetupException(Exception):
    pass


@app.command()
def lint(line_len=conf.line_len, full: bool = False):
    target = "." if full else conf.module_path
    check_call(["black", target, "-l", line_len])
    check_call(["isort", target, "--profile", "black", "-l", line_len])
    check_call(["flake8", target, "--max-line-length", line_len])


@app.command()
def init(
    input: bool = True,
    docs: bool = False,
    notebooks: bool = False,
    actions: bool = False,
    single_file: bool = False,
    git: bool = True,
):
    res_dir = cookiecutter(cc_repo, no_input=not input)
    os.chdir(res_dir)
    _cleanup(docs, actions, notebooks, single_file)
    if not git:
        return
    for cmd in [
        ["init"],
        ["add", "*"],
        ["commit", "-m", "init"],
        ["branch", "template"],
    ]:
        check_call(["git", *cmd])


@app.command()
def update_boilerplate(merge: bool = False):

    author_base = conf.project_conf["authors"][0]
    if isinstance(author_base, dict):
        name = author_base["name"]
        email = author_base["email"]
        url = conf.project_conf["urls"]["Homepage"]
        pykey = "requires-python"
        description = conf.module.__doc__
    else:
        warn("legacy pyproject.toml! fill in email and delete some files")
        name = author_base
        email = "FILL@ME"
        url = conf.project_conf["url"]
        pykey = "python"
        description = conf.project_conf["description"]

    cc_context = {
        "full_name": name,
        "email": email,
        "github_user": url.split("/")[-2],
        "project_name": conf.name,
        "description": description,
        "python_version": conf.project_conf[pykey][2:],
    }

    branch = _get_branch()
    check_call(["git", "checkout", "template"])
    cookiecutter(
        cc_repo,
        no_input=True,
        extra_context=cc_context,
        output_dir="..",
        overwrite_if_exists=True,
    )

    single = conf.module_path.endswith(".py")
    _cleanup(Path(docdir).exists(), Path(".github").exists(), nb_dir.exists(), single)
    adds = check_output(["git", "add", "*"]).strip()
    if adds:
        check_call(["git", "commit", "-m", "update-boilerplate"])
    if merge:
        check_call(["git", "checkout", branch])
        check_call(["git", "merge", "template", "--no-edit"])


@app.command()
def test(html: bool = False, v: bool = False, notebooks: bool = True, cov: bool = True):
    lint()
    test_paths = [conf.module_path]
    test_notebook_path = Path("test_nb_integrations.py")
    if notebooks:
        test_notebook_path.write_text("\n\n".join(get_nb_scripts()))
        test_paths.append(test_notebook_path.as_posix())
    comm = ["python", "-m", "pytest", *test_paths, "--doctest-modules"]
    opt_dic = {f"--cov={conf.module_path}": cov, "--cov-report=html": html, "-s": v}
    for commstr, _ in filter(lambda it: it[1], opt_dic.items()):
        comm.append(commstr)

    try:
        check_call(comm)
    finally:
        test_notebook_path.unlink(missing_ok=True)


@app.command()
def build_docs():
    _nbs = [*map(str, get_notebooks())]
    if _nbs:
        out = f"--output-dir={docdir}/notebooks"
        check_call(["jupyter", "nbconvert", *_nbs, "--to", "rst", out])
    check_call(["sphinx-build", docdir, f"{docdir}/_build"])


@app.command()
def tag():
    branch = _get_branch()
    if branch != "main":
        raise SetupException(f"only main branch can be tagged - {branch}")

    tag_version = f"v{conf.version}"
    tags = check_output(["git", "tag"]).split()
    if tag_version in tags:
        raise SetupException(f"{tag_version} version already tagged")
    if Path(docdir).exists():
        notes = current_release_path.read_text()
        note_rst = f"{tag_version}\n------\n\n" + notes
        Path(docdir, "release_notes", f"{tag_version}.rst").write_text(note_rst)
        build_docs()
        current_release_path.write_text("")
        check_call(["git", "add", "docs"])
        check_call(["git", "commit", "-m", f"docs for {tag_version}"])
    else:
        notes = tag_version

    check_call(["git", "tag", "-a", tag_version, "-m", notes])
    check_call(["git", "push"])
    check_call(["git", "push", "origin", tag_version])


def _get_branch():
    comm = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    return check_output(comm).strip().decode("utf-8")


def _cleanup(leave_docs, leave_actions, leave_notebooks, single_file):
    if not leave_docs:
        rmtree(docdir)
        Path(".readthedocs.yml").unlink()
    if not leave_actions:
        rmtree(".github")
    if not leave_notebooks:
        rmtree(nb_dir)
    if single_file:
        pack_dir = Path(conf.name)
        init_str = (pack_dir / "__init__.py").read_text()
        rmtree(pack_dir)
        Path(f"{conf.name}.py").write_text(init_str)
