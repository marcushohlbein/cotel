from repo_intel.parsers.javascript_parser import JavaScriptParser


def test_parse_function():
    code = """
function helloWorld() {
    console.log('hello');
}
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "helloWorld"


def test_parse_class():
    code = """
class MyClass {
    method() {
        // ...
    }
}
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyClass" in symbols
    assert symbols["MyClass"].kind == "class"


def test_parse_arrow_function():
    code = """
const arrowFunc = () => {
    return 42;
};
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    arrow_symbols = [s for s in result.symbols if s.name == "arrowFunc"]
    assert len(arrow_symbols) == 1


def test_parse_endpoint():
    code = """
app.get('/users', (req, res) => {
    res.json([]);
});
"""
    parser = JavaScriptParser()
    result = parser.parse(code, "test_file")

    endpoints = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoints) == 1
    assert endpoints[0].http_method == "GET"
    assert endpoints[0].path == "/users"
