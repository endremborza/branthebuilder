"""Render the bundled template: each `{{field}}` of `Context` in paths and contents."""

import datetime as dt
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .vars import GITHUB_DIR, OSC_PATH, TEMPLATE_DIR, WORKFLOW_DIR

# paths earlier templates produced; update-boilerplate removes them from `template`
RETIRED = ((WORKFLOW_DIR / "twine_release.yml").as_posix(), ".readthedocs.yml")


@dataclass(frozen=True)
class Context:
    name: str
    description: str
    author: str
    email: str
    github_user: str
    python_version: str
    year: str = field(default_factory=lambda: str(dt.date.today().year))


@dataclass(frozen=True)
class Layout:
    actions: bool
    os_compatibility: bool
    single_file: bool


def _fill(text: str, ctx: Context) -> str:
    for key, value in asdict(ctx).items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def render(ctx: Context, layout: Layout) -> dict[str, str]:
    """Relative posix path → content of every file the project gets."""
    files = {
        _fill(p.relative_to(TEMPLATE_DIR).as_posix(), ctx): _fill(
            p.read_text(encoding="utf-8"), ctx
        )
        for p in TEMPLATE_DIR.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    if not layout.actions:
        files = {k: v for k, v in files.items() if not k.startswith(f"{GITHUB_DIR}/")}
    elif not layout.os_compatibility:
        del files[OSC_PATH.as_posix()]
    if layout.single_file:
        package = f"{ctx.name}/"
        init = files[f"{package}__init__.py"]
        files = {k: v for k, v in files.items() if not k.startswith(package)}
        files[f"{ctx.name}.py"] = init
        files["pyproject.toml"] = files["pyproject.toml"].replace(
            f"{package}__init__.py", f"{ctx.name}.py"
        )
    return files


def write(files: dict[str, str], root: Path) -> None:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
