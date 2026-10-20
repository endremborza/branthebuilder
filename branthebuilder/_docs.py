"""Write a module's API reference as markdown: `python -I _docs.py <module> <out.md>`.

Stdlib only: branb runs it with the project's own interpreter, so the module is
imported in its own environment.
"""

import importlib
import inspect
import sys
from pathlib import Path


def _section(level: str, title: str, obj: object) -> list[str]:
    lines = ["", f"{level} `{title}`"]
    if obj.__doc__:
        lines.append(obj.__doc__.strip())
    return lines


def api_lines(name: str) -> list[str]:
    module = importlib.import_module(name)
    lines = [f"# {name}"]
    if module.__doc__:
        lines += ["", module.__doc__.strip()]
    for attr, obj in sorted(inspect.getmembers(module)):
        local = (getattr(obj, "__module__", None) or "").startswith(name)
        if attr.startswith("_") or not local:
            continue
        if inspect.isfunction(obj):
            lines += _section("##", f"{attr}{inspect.signature(obj)}", obj)
        elif inspect.isclass(obj):
            lines += _section("##", attr, obj)
            for mname, mobj in sorted(inspect.getmembers(obj, inspect.isfunction)):
                if not mname.startswith("_"):
                    lines += _section("###", f"{mname}{inspect.signature(mobj)}", mobj)
    return lines


if __name__ == "__main__":
    module, out = sys.argv[1:]
    Path(out).parent.mkdir(exist_ok=True)
    Path(out).write_text("\n".join(api_lines(module)) + "\n", encoding="utf-8")
