from branthebuilder import (
    __version__,
    clean,
    django,
    docs,
    misc,
    release,
    sonar,
    test,
)


def test_import():
    assert isinstance(__version__, str)


def test_modules():
    for m in [clean, django, docs, misc, release, sonar, test]:
        assert callable(m.task)
