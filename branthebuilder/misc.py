import io
import re

from cookiecutter.main import cookiecutter
from invoke import task

from .constants import cc_repo
from .vars import package_name, pytom


@task
def lint(c, add=False):
    # this should be added to pre-commit hook
    with io.StringIO() as f:
        c.run(r"black . -l 79 --exclude \.*venv --exclude data", err_stream=f)
        blackout = f.getvalue().strip()

    with io.StringIO() as f:
        c.run(f"isort {package_name} -m 3 --tc", out_stream=f)
        isout = f.getvalue().strip()

    c.run(f"flake8 {package_name}")

    fixed_files = re.compile("reformatted (.*)").findall(
        blackout
    ) + re.compile("Fixing (.*)").findall(isout)
    if add and fixed_files:
        c.run(f"git add {' '.join(set(fixed_files))}")
    else:
        print(fixed_files)


@task
def update_boilerplate(c, merge=False):

    cc_context = {
        "full_name": pytom["project"]["authors"][0],
        "github_user": pytom["project"]["url"].split("/")[-2],
        "project_name": pytom["project"]["name"],
        "description": pytom["project"]["description"],
        "python_version": pytom["project"]["python"][2:],
    }

    with io.StringIO() as f:
        c.run("git rev-parse --abbrev-ref HEAD", out_stream=f)
        branch = f.getvalue().strip()
    c.run("git checkout template")
    cookiecutter(
        cc_repo,
        no_input=True,
        extra_context=cc_context,
        output_dir="..",
        overwrite_if_exists=True,
    )
    c.run("git add *")
    c.run('git commit -m "update-boilerplate"')
    if merge:
        c.run(f"git checkout {branch}")
        c.run("git merge template --no-edit")


@task
def notebook(c):
    c.run(
        "jupyter notebook "
        "--NotebookApp.kernel_spec_manager_class="
        "branthebuilder.notebook_runner.SysInsertManager"
    )
