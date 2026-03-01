import pytest
from repo_intel.parsers.go_parser import GoParser


def test_parse_function():
    code = """
package main

func helloWorld() {
    fmt.Println("Hello")
}

func ExportedFunc() {
    fmt.Println("Exported")
}
"""
    parser = GoParser()
    result = parser.parse(code, "test_file")

    assert len(result.symbols) >= 2
    symbols = {s.name: s for s in result.symbols}
    assert "helloWorld" in symbols
    assert "ExportedFunc" in symbols
    assert symbols["ExportedFunc"].exported == True


def test_parse_struct():
    code = """
type User struct {
    Name string
}

func (u *User) Get() string {
    return u.Name
}
"""
    parser = GoParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "User" in symbols
    assert symbols["User"].kind == "class"
    assert "Get" in symbols
    assert symbols["Get"].kind == "method"


def test_parse_interface():
    code = """
type MyInterface interface {
    Method()
}
"""
    parser = GoParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyInterface" in symbols
    assert symbols["MyInterface"].kind == "interface"


def test_parse_imports():
    code = """
import (
    "fmt"
    "os"
)
"""
    parser = GoParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) >= 2
