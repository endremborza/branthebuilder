import os

from invoke import task

from .vars import conf


@task
def clean(
    c,
    build=False,
    test=False,
    sonar=False,
):
    patterns = []
    if build:
        patterns += ["build", f"{conf.name}.egg-info", "**/*.pyc"]
    if sonar:
        patterns += [
            os.path.join(conf.name, s)
            for s in [".sonar", ".scannerwork", "sonar-project.properties"]
        ]
    if test:
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
def purge(c):
    clean(c, True, True, True)
