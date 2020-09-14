import os

from invoke import task

from .vars import package_name


@task
def clean(
    c,
    docs=False,
    build=False,
    bytecode=False,
    test=False,
    sonar=False,
    everything=False,
):
    patterns = []
    if docs or everything:
        patterns.append("docs")
    if build or everything:
        patterns += ["build", f"{package_name}.egg-info"]
    if bytecode or everything:
        patterns.append("**/*.pyc")
    if sonar or everything:
        patterns += [
            os.path.join(package_name, s)
            for s in [".sonar", ".scannerwork", "sonar-project.properties"]
        ]
    if test or everything:
        patterns += [
            ".pytest_cache",
            ".coverage",
            "**/.coverage",
            "htmlcov",
            "**/coverage.xml",
        ]

    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task
def prune(c):
    clean(c, everything=True)
