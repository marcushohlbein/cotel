import pytest
from repo_intel.parsers.rust_parser import RustParser


def test_parse_function():
    code = """
fn hello_world() {
    println!("Hello");
}
"""
    parser = RustParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) == 1
    assert result.symbols[0].name == "hello_world"
    assert result.symbols[0].kind == "function"


def test_parse_struct():
    code = """
struct MyStruct {
    field: i32,
}

impl MyStruct {
    fn new() -> Self {
        Self { field: 0 }
    }
}
"""
    parser = RustParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyStruct" in symbols
    assert symbols["MyStruct"].kind == "class"
    assert "new" in symbols
    assert symbols["new"].kind == "method"


def test_parse_trait():
    code = """
trait MyTrait {
    fn method(&self);
}
"""
    parser = RustParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyTrait" in symbols
    assert symbols["MyTrait"].kind == "interface"


def test_parse_use_statement():
    code = """
use std::collections::HashMap;
use std::fs::File;
"""
    parser = RustParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) == 2


def test_public_function():
    code = """
pub fn public_func() {
}

fn private_func() {
}
"""
    parser = RustParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert symbols["public_func"].exported == True
    assert symbols["private_func"].exported == False
