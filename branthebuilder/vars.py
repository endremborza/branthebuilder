import importlib
from functools import cached_property

import toml

doc_dir_name = "docs"
doctest_notebooks_glob = "notebooks/doc-*.ipynb"


class PackageConf:
    @cached_property
    def pytom(self):
        return toml.load("pyproject.toml")

    @property
    def project_conf(self):
        return self.pytom["project"]

    @property
    def name(self):
        return self.project_conf["name"]

    @property
    def line_len(self):
        return self.pytom["tool"]["bran"]["line-length"]

    @property
    def author(self):
        return " - ".join(self.project_conf["authors"])


conf = PackageConf()


def get_version():
    return importlib.import_module(conf.name).__version__
