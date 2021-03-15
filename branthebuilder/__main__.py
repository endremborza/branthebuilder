import subprocess

from cookiecutter.main import cookiecutter

cc_repo = "https://github.com/endremborza/python-boilerplate-v2"


if __name__ == "__main__":
    res_dir = cookiecutter(cc_repo)
    subprocess.check_call(["git", "init"], cwd=res_dir)
    subprocess.check_call(["git", "add", "*"], cwd=res_dir)
    subprocess.check_call(
        ["git", "commit", "-m", "setup using template"], cwd=res_dir
    )
    subprocess.check_call(["git", "branch", "template"], cwd=res_dir)
