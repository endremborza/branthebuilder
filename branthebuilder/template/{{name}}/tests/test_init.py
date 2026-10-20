from {{name}} import __version__


def test_import():
    assert isinstance(__version__, str)
