import re
import tomllib
from pathlib import Path
from typing import Literal

README_PATH = Path("README.md")
CFF_PATH = Path("CITATION.cff")
DOC_DIR = Path("docs")
NOTES_PATH = DOC_DIR / "release_notes.md"
TEST_DIR = Path("tests")
GITHUB_DIR = Path(".github")
WORKFLOW_DIR = GITHUB_DIR / "workflows"
OSC_PATH = WORKFLOW_DIR / "compatibility_test.yml"
TEMPLATE_DIR = Path(__file__).parent / "template"
TEMPLATE_BRANCH = "template"

ORCID_DIC_ENV = "ORCID_MAP"
PYTHON_VERSION = "3.11"

Bump = Literal["major", "minor", "bug"]


def bumped(version: str, bump: Bump) -> str:
    """
    >>> [bumped("1.2.3", b) for b in ("major", "minor", "bug")]
    ['2.0.0', '1.3.0', '1.2.4']
    """
    major, minor, bug = map(int, version.split("."))
    parts = {
        "major": (major + 1, 0, 0),
        "minor": (major, minor + 1, 0),
        "bug": (major, minor, bug + 1),
    }[bump]
    return ".".join(map(str, parts))


class PackageConf:
    """The project in the working directory, re-read on each access to follow chdir."""

    @property
    def project_conf(self) -> dict:
        with open("pyproject.toml", "rb") as f:
            return tomllib.load(f)["project"]

    @property
    def name(self) -> str:
        return self.project_conf["name"]

    @property
    def module_path(self) -> str:
        return self.name if Path(self.name).exists() else f"{self.name}.py"

    @property
    def version_file(self) -> Path:
        path = Path(self.module_path)
        return path / "__init__.py" if path.is_dir() else path

    @property
    def version(self) -> str:
        return re.findall('__version__ = "(.*)"', self.version_file.read_text())[0]

    def write_version(self, version: str) -> None:
        text = self.version_file.read_text()
        self.version_file.write_text(
            text.replace(
                f'__version__ = "{self.version}"', f'__version__ = "{version}"'
            )
        )


conf = PackageConf()
