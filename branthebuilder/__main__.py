import subprocess
from pathlib import Path

from cookiecutter.main import cookiecutter

from .constants import cc_repo


def write_command(path, cmd):
    path.write_text("\n".join(["#!/bin/sh", cmd]))


if __name__ == "__main__":
    res_dir = cookiecutter(cc_repo)
    for cmd in [
        ["git", "init"],
        ["git", "add", "*"],
        ["git", "commit", "-m", "setup using template"],
        ["git", "branch", "template"],
    ]:
        subprocess.check_call(cmd, cwd=res_dir)
    prec_hook = Path(res_dir, ".git", "hooks", "pre-commit")
    msg_hook = Path(res_dir, ".git", "hooks", "commit-msg")
    write_command(prec_hook, "inv lint --add")
    write_command(
        msg_hook, 'echo "- `cat $1`" >> docs_config/current_release.rst'
    )

    for hook in [prec_hook, msg_hook]:
        subprocess.check_call(["chmod", "+x", hook.as_posix()])
