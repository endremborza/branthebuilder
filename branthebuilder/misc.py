import io

from cookiecutter.main import cookiecutter
from invoke import task

from .constants import cc_repo
from .vars import boilerplate_branch, package_name, pytom


@task
def lint(c):
    c.run(r"black . -l 79 --exclude \.*venv")
    c.run(f"isort {package_name} -m 3 --tc")
    c.run(f"flake8 {package_name}")


@task
def update_boilerplate(c):  # TODO: maybe drop template package folder

    cc_context = {
        "full_name": pytom["project"]["authors"][0],
        "github_user": pytom["project"]["url"].split("/")[-2],
        "project_name": pytom["project"]["name"],
        "python_version": pytom["project"]["python"][2:],
    }

    f = io.StringIO()
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
    c.run(f"git checkout {branch}")
    c.run(f"git merge template --no-edit")


@task
def notebook(c):
    c.run(
        "jupyter notebook "
        "--NotebookApp.kernel_spec_manager_class="
        "branthebuilder.notebook_runner.SysInsertManager"
    )
