import importlib
from pathlib import Path
from warnings import warn

import toml

README_PATH = Path("README.md")
CFF_PATH = Path("CITATION.cff")
DOC_DIR = Path("docs")

ORCID_DIC_ENV = "ORCID_MAP"

cc_repo = "https://github.com/endremborza/python-boilerplate-v2"

_D = {"project": {"name": ".", "author": []}, "tool": {"branb": {"line-length": 88}}}


class PackageConf:
    @property
    def pytom(self):
        try:
            return toml.load("pyproject.toml")
        except FileNotFoundError:
            warn(f"not in project directory, using defaults {_D}")
            return _D

    @property
    def project_conf(self):
        return self.pytom["project"]

    @property
    def name(self):
        return self.project_conf["name"]

    @property
    def module_path(self):
        if Path(self.name).exists():
            return self.name
        return f"{self.name}.py"

    @property
    def line_len(self):
        return str(self.pytom["tool"]["branb"]["line-length"])

    @property
    def module(self):
        return importlib.import_module(self.name)

    @property
    def version(self):
        return self.module.__version__


conf = PackageConf()
