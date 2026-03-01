from repo_intel.parsers.python_parser import PythonParser
from repo_intel.parsers.javascript_parser import JavaScriptParser


def get_parser(language: str):
    """Get parser instance for language."""
    parsers = {
        "python": PythonParser,
        "javascript": lambda: JavaScriptParser("javascript"),
        "typescript": lambda: JavaScriptParser("typescript"),
    }

    parser_class = parsers.get(language)
    if parser_class:
        return parser_class() if callable(parser_class) else parser_class

    return None
