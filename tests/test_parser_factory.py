from repo_intel.parsers.factory import get_parser


def test_get_python_parser():
    parser = get_parser("python")
    assert parser is not None
    assert hasattr(parser, "parse")


def test_get_javascript_parser():
    parser = get_parser("javascript")
    assert parser is not None


def test_get_typescript_parser():
    parser = get_parser("typescript")
    assert parser is not None


def test_unsupported_language():
    parser = get_parser("cobol")
    assert parser is None
