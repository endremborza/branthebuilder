import glob
import json
import os

from invoke import task

from .vars import doctest_notebooks_glob, package_name

test_root = os.path.join(package_name, "tests")
test_notebook_path = os.path.join(test_root, "test_nb_integrations.py")
cov_xmlpath = f"{package_name}/coverage.xml"


def _get_nb_scripts():
    new_test_scripts = []
    for nb_idx, nb_file in enumerate(glob.glob(doctest_notebooks_glob)):
        nb_dic = json.load(open(nb_file))
        nb_code = "\n".join(
            [
                "\n".join(c["source"])
                for c in nb_dic["cells"]
                if (c["cell_type"] == "code")
            ]
        )
        if len(nb_code) > 0:
            new_test_scripts.append(
                f"def test_nb_integration_{nb_idx}():\n"
                + "\n".join([f"    {s}" for s in nb_code.split("\n")])
            )
    return new_test_scripts


@task
def test(c, html=False, xml=False, notebook_tests=True):

    comm = f"python -m pytest {package_name} --cov={package_name}"
    if html:
        comm += " --cov-report=html"
    elif xml:
        comm += f" --cov-report=xml:{cov_xmlpath}"

    if notebook_tests:
        if not os.path.exists(test_root):
            os.makedirs(test_root)
        new_test_scripts = _get_nb_scripts()
        with open(test_notebook_path, "w") as fp:
            fp.write("\n\n".join(new_test_scripts))

    try:
        c.run(comm)
    finally:
        c.run(f"rm {package_name}/tests/test_nb_integrations.py")


@task
def clean(c):
    c.run(f"rm -f {cov_xmlpath}")
    c.run("rm -rf htmlcov")
    c.run("rm -rf .pytest_cache")
    c.run("rm -f .coverage")
