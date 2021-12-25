import glob
import json
import os

from invoke import task

from .misc import lint
from .vars import conf, doctest_notebooks_glob


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


@task(pre=[lint])
def test(c, html=False, xml=False, v=False, notebook_tests=True):

    test_root = os.path.join(conf.name, "tests")
    test_notebook_path = os.path.join(test_root, "test_nb_integrations.py")
    cov_xmlpath = f"{conf.name}/coverage.xml"

    comm = f"python -m pytest {conf.name} --cov={conf.name}"
    if html:
        comm += " --cov-report=html"
    elif xml:
        comm += f" --cov-report=xml:{cov_xmlpath}"

    if v:
        comm += " -s"

    if notebook_tests:
        if not os.path.exists(test_root):
            os.makedirs(test_root)
        new_test_scripts = _get_nb_scripts()
        with open(test_notebook_path, "w") as fp:
            fp.write("\n\n".join(new_test_scripts))

    try:
        c.run(comm)
    finally:
        c.run(f"rm {conf.name}/tests/test_nb_integrations.py")
