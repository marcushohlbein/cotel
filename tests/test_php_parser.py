import pytest
from repo_intel.parsers.php_parser import PHPParser


def test_parse_function():
    code = """<?php
function helloWorld() {
    echo "Hello";
}
"""
    parser = PHPParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "helloWorld"
    assert result.symbols[0].kind == "function"


def test_parse_class():
    code = """<?php
class MyClass {
    public function myMethod() {
        return "value";
    }
}
"""
    parser = PHPParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyClass" in symbols
    assert symbols["MyClass"].kind == "class"
    assert "myMethod" in symbols
    assert symbols["myMethod"].kind == "method"


def test_parse_interface():
    code = """<?php
interface MyInterface {
    public function method();
}
"""
    parser = PHPParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyInterface" in symbols
    assert symbols["MyInterface"].kind == "interface"


def test_parse_laravel_endpoint():
    code = """<?php
class UserController extends Controller {
    public function index() {
        return User::all();
    }
    
    public function store() {
        // Store user
    }
}
"""
    parser = PHPParser()
    result = parser.parse(code, "test_file")

    # Laravel's index method should be detected as GET endpoint
    endpoints = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoints) >= 1


def test_parse_namespace():
    code = r"""
use App\Models\User;
use App\Http\Controllers\Controller;
"""
    parser = PHPParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) == 2
