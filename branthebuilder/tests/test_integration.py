import os
import sys
from pathlib import Path
from subprocess import check_call

import pytest

import branthebuilder.main as ns
from branthebuilder.vars import CFF_PATH, README_PATH


@pytest.mark.parametrize(
    "docs,nb,single_file,actions",
    [
        (True, True, False, True),
        (False, False, True, False),
        (True, False, True, False),
    ],
)
def test_integration(tmp_path, docs, nb, single_file, actions):
    os.chdir(tmp_path)
    check_call(["git", "init", "remote"])
    os.chdir("remote")
    check_call(["git", "config", "receive.denyCurrentBranch", "ignore"])
    os.chdir(tmp_path)
    ns.init(False, docs, nb, actions, single_file)
    if single_file:
        with Path("testproject.py").open("a") as f:
            f.write(DOCTESTED_FUN)

    check_call(["git", "remote", "add", "origin", "../remote"])
    check_call(["git", "push", "--set-upstream", "origin", "main"])
    sys.path.insert(0, Path(tmp_path, "testproject").as_posix())
    ns.lint()
    ns.test(True, True, True)
    d1 = 1238979
    ns.add_zenodo_concept_doi(d1)
    assert str(d1) in README_PATH.read_text()
    ns.init_cff()
    d2 = 7658979
    ns.add_zenodo_concept_doi(d2)
    assert str(d1) not in README_PATH.read_text()
    assert str(d2) in README_PATH.read_text()
    assert str(d2) in CFF_PATH.read_text()
    ns.tag("tag msg")
    check_call(["flit", "build"])
    ns.update_boilerplate(True)


def test_errs(tmp_path):
    os.chdir(tmp_path)
    ns.init(False)


DOCTESTED_FUN = '''
def fing(x):
    """add two
    >>> fing(3)
    5
    """
    return x + 2
'''
