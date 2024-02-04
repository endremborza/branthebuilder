import importlib
import re
from enum import Enum
from pathlib import Path
from warnings import warn

import toml

README_PATH = Path("README.md")
CFF_PATH = Path("CITATION.cff")
DOC_DIR = Path("docs")

ORCID_DIC_ENV = "ORCID_MAP"

cc_repo = "https://github.com/endremborza/python-boilerplate-v2"

_D = {"project": {"name": ".", "author": []}, "tool": {"branb": {"line-length": 88}}}


class Bump(Enum):
    major = "major"
    minor = "minor"
    bug = "bug"


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
        module = importlib.import_module(self.name)
        return importlib.reload(module)

    @property
    def version(self):
        return re.findall('__version__ = "(.*)"', self.version_file.read_text())[0]

    @property
    def version_file(self):
        if Path(self.name).exists():
            return Path(self.name, "__init__.py")
        else:
            return Path(f"{self.name}.py")

    def get_bumped_version(self, bump: Bump):

        old_v = self.version
        major, minor, bug = map(int, old_v.split("."))
        if bump == Bump.major:
            major += 1
        elif bump == Bump.minor:
            minor += 1
        elif bump == Bump.bug:
            bug += 1
        else:
            raise ValueError(f"wrong kind of bump {bump}")
        new_v = ".".join(map(str, (major, minor, bug)))
        self.version_file.write_text(
            self.version_file.read_text().replace(
                f'__version__ = "{old_v}"', f'__version__ = "{new_v}"'
            )
        )
        return new_v


conf = PackageConf()
