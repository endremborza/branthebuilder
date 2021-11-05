import importlib

import toml

pytom = toml.load("pyproject.toml")
package_name = pytom["project"]["name"]
author_name = " - ".join(pytom["project"]["authors"])

doc_dir_name = "docs"
doctest_notebooks_glob = "notebooks/doc-*.ipynb"


def get_version():
    return importlib.import_module(package_name).__version__


LINE_LENGTH = pytom["tool"]["bran"]["line-length"]
