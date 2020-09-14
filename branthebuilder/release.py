import io

from invoke import task

from .vars import mymodule

version = mymodule.__version__


@task
def new(c):
    c.run("python setup.py sdist")
    c.run("twine check dist/*")
    c.run(
        f"twine upload dist/*{version}.tar.gz -u __token__ -p $TWINE_PASSWORD"
    )


@task
def tag(c):
    f = io.StringIO()
    c.run("git rev-parse --abbrev-ref HEAD", out_stream=f)
    branch = f.getvalue().strip()
    f.close()

    if branch == "master":
        tag_version = f"v{version}"
        f2 = io.StringIO()
        c.run("git tag", out_stream=f2)
        tags = f2.getvalue().split()
        print(tags)
        if tag_version not in tags:
            current_release_path = "docs_config/current_release.rst"
            with open(current_release_path) as fp:
                notes = fp.read()
            with open(
                f"docs_config/release_notes/{tag_version}.rst", "w"
            ) as fp:
                fp.write(notes)
            c.run(f"git tag -a {tag_version} -m '{notes}'")
            with open(current_release_path, "w") as fp:
                fp.write("")
            c.run("git push --tags")
        else:
            print(f"{tag_version} version already tagged")
    else:
        print("only master branch can be tagged")
