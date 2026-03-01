from repo_intel.parsers.python_parser import PythonParser
from repo_intel.parsers.javascript_parser import JavaScriptParser
from repo_intel.parsers.java_parser import JavaParser
from repo_intel.parsers.rust_parser import RustParser
from repo_intel.parsers.go_parser import GoParser
from repo_intel.parsers.php_parser import PHPParser


def get_parser(language: str):
    """Get parser instance for language."""
    parsers = {
        "python": PythonParser,
        "javascript": lambda: JavaScriptParser("javascript"),
        "typescript": lambda: JavaScriptParser("typescript"),
        "java": JavaParser,
        "rust": RustParser,
        "go": GoParser,
        "php": PHPParser,
    }

    parser_class = parsers.get(language)
    if parser_class:
        return parser_class() if callable(parser_class) else parser_class

    return None
