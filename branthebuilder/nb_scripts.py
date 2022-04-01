import json
from pathlib import Path

nb_dir = Path("notebooks")


def get_notebooks():
    return sorted(nb_dir.glob("doc-*.ipynb"))


def get_nb_scripts():
    for nb_idx, nb_file in enumerate(get_notebooks()):
        nb_dic = json.load(open(nb_file))
        code_cells = filter(lambda c: c["cell_type"] == "code", nb_dic["cells"])
        nb_lines = [line for c in code_cells for line in c["source"]]
        if not nb_lines:
            continue
        yield (
            f"def test_nb_integration_{nb_idx}():\n"
            + "\n".join([f"    {s}" for s in nb_lines])
        )
