import subprocess

from cookiecutter.main import cookiecutter

from .constants import cc_repo

if __name__ == "__main__":
    res_dir = cookiecutter(cc_repo)
    subprocess.check_call(["git", "init"], cwd=res_dir)
    subprocess.check_call(["git", "add", "*"], cwd=res_dir)
    subprocess.check_call(
        ["git", "commit", "-m", "setup using template"], cwd=res_dir
    )
    subprocess.check_call(["git", "branch", "template"], cwd=res_dir)
