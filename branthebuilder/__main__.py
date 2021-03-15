import os
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
    prec_hook = os.path.join(res_dir, ".git", "hooks", "pre-commit")
    msg_hook = os.path.join(res_dir, ".git", "hooks", "commit-msg")
    with open(prec_hook, "w") as fp:
        fp.write("#!/bin/sh\n")
        fp.write("inv misc.lint --add")

    with open(msg_hook, "w") as fp:
        fp.write("#!/bin/sh\n")
        fp.write('echo "- `cat $1`" >> docs_config/current_release.rst')

    try:
        subprocess.check_call(["chmod", "+x", prec_hook])
    finally:
        pass
