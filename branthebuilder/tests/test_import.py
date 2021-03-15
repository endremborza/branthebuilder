from branthebuilder import __version__


def test_import():
    assert isinstance(__version__, str)


def test_modules():
    from branthebuilder import clean, django, docs, misc, release, sonar, test
