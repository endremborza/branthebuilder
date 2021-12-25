import io
import re

from cookiecutter.main import cookiecutter
from invoke import task

from .constants import cc_repo
from .vars import conf


@task
def lint(c, add=False):

    with io.StringIO() as f:
        c.run(f"black {conf.name} -l {conf.line_len}", err_stream=f)
        blackout = f.getvalue().strip()

    with io.StringIO() as f:
        c.run(
            f"isort {conf.name} --profile black -l {conf.line_len}",
            out_stream=f,
        )
        isout = f.getvalue().strip()

    c.run(f"flake8 {conf.name} --max-line-length {conf.line_len}")

    fixed_files = re.compile("reformatted (.*)").findall(
        blackout
    ) + re.compile("Fixing (.*)").findall(isout)
    if add and fixed_files:
        c.run(f"git add {' '.join(set(fixed_files))}")
    else:
        print("fixed files: \n", "\n".join(fixed_files))


@task
def update_boilerplate(c, merge=False):

    cc_context = {
        "full_name": conf.project_conf["authors"][0],
        "github_user": conf.project_conf["url"].split("/")[-2],
        "project_name": conf.project_conf["name"],
        "description": conf.project_conf["description"],
        "python_version": conf.project_conf["python"][2:],
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
