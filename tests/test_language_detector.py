from repo_intel.utils.language_detector import detect_language


def test_python_detection():
    assert detect_language("test.py") == "python"
    assert detect_language("test.pyi") == "python"


def test_javascript_detection():
    assert detect_language("test.js") == "javascript"
    assert detect_language("test.jsx") == "javascript"


def test_typescript_detection():
    assert detect_language("test.ts") == "typescript"
    assert detect_language("test.tsx") == "typescript"


def test_java_detection():
    assert detect_language("Test.java") == "java"


def test_rust_detection():
    assert detect_language("main.rs") == "rust"


def test_go_detection():
    assert detect_language("main.go") == "go"


def test_php_detection():
    assert detect_language("index.php") == "php"


def test_unknown_detection():
    assert detect_language("README.md") is None
