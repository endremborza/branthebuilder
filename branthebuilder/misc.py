from invoke import task

from .vars import boilerplate_branch, package_name, pytom


@task
def lint(c):
    c.run(r"black . -l 79 --exclude \.*venv")
    c.run(f"isort {package_name} -m 3 --tc")
    c.run(f"flake8 {package_name}")


@task
def update_boilerplate(c):  # TODO: maybe drop template package folder

    ck_context = {
        "full_name": pytom["project"]["authors"][0],
        "github_user": pytom["project"]["url"].split("/")[-2],
        "project_name": pytom["project"]["name"],
        "python_version": pytom["project"]["python"][2:],
    }

    c.run("git fetch boilerplate")
    c.run(f"git merge boilerplate/{boilerplate_branch} --no-edit")


@task
def notebook(c):
    c.run(
        "jupyter notebook "
        "--NotebookApp.kernel_spec_manager_class="
        "branthebuilder.notebook_runner.SysInsertManager"
    )
