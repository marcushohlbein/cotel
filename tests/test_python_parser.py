from repo_intel.parsers.python_parser import PythonParser


def test_parse_function():
    code = """
def hello_world():
    print('hello')
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "hello_world"
    assert result.symbols[0].kind == "function"


def test_parse_class():
    code = """
class MyClass:
    def method(self):
        pass
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyClass" in symbols
    assert symbols["MyClass"].kind == "class"
    assert "method" in symbols
    assert symbols["method"].kind == "method"


def test_parse_imports():
    code = """
import os
from sys import argv
from collections import defaultdict
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) == 3
    imports = [i.module for i in result.imports]
    assert "os" in imports
    assert "sys" in imports
    assert "collections" in imports


def test_parse_decorator_endpoint():
    code = """
from flask import Flask
app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    pass
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    endpoint_symbols = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoint_symbols) == 1
    assert endpoint_symbols[0].name == "get_users"
    assert endpoint_symbols[0].http_method == "GET"
    assert endpoint_symbols[0].path == "/users"


def test_function_calls():
    code = """
def caller():
    callee()
"""
    parser = PythonParser()
    result = parser.parse(code, "test_file")

    call_relations = [r for r in result.relations if r.relation_type == "calls"]
    assert len(call_relations) == 1
