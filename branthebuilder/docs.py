import glob
import os

from invoke import task

from .vars import (
    author_name,
    doc_dir_name,
    doctest_notebooks_glob,
    package_name,
)


@task
def setup(c):
    c.run(
        f"sphinx-quickstart {doc_dir_name} -p {package_name} "
        f'-a "{author_name}" -q --ext-autodoc'
    )
    c.run("cp -r docs_config/* docs/")
    c.run("rm docs/current_release.rst")
    c.run("pip install -r docs/requirements.txt")


@task
def build(c):

    c.run("cp -r docs_config/release_notes/* docs/release_notes")

    doc_notebooks = sorted(glob.glob(doctest_notebooks_glob))
    _doc_nbs_string = " ".join(doc_notebooks)
    c.run(
        f"jupyter nbconvert --to rst {_doc_nbs_string} "
        f"--output-dir={doc_dir_name}/notebooks"
    )
    toc_nbs = [
        f"   notebooks/{os.path.split(nbp)[-1].split('.')[0]}"
        for nbp in doc_notebooks
    ]
    _toc_nb_lines = "\n".join(toc_nbs)
    index_rst = f"""
Welcome to {package_name}'s documentation!
=====================================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

{_toc_nb_lines}
   autosumm
   release_notes/main

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    autosumm_rst = f"""

API
===

.. automodapi:: {package_name}

"""

    with open(os.path.join(doc_dir_name, "index.rst"), "w") as fp:
        fp.write(index_rst)

    with open(os.path.join(doc_dir_name, "autosumm.rst"), "w") as fp:
        fp.write(autosumm_rst)

    c.run("sphinx-build docs docs/_build")


@task
def purge(c):
    c.run("rm -rf docs")
