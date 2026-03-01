import pytest
from repo_intel.parsers.java_parser import JavaParser


def test_parse_method():
    code = """
public class Test {
    public void hello() {
        System.out.println("Hello");
    }
}
"""
    parser = JavaParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "Test" in symbols
    assert symbols["Test"].kind == "class"
    assert "hello" in symbols
    assert symbols["hello"].kind == "method"


def test_parse_interface():
    code = """
public interface MyInterface {
    void method();
}
"""
    parser = JavaParser()
    result = parser.parse(code, "test_file")

    symbols = {s.name: s for s in result.symbols}
    assert "MyInterface" in symbols
    assert symbols["MyInterface"].kind == "interface"


def test_parse_imports():
    code = """
import java.util.List;
import java.util.Map;
"""
    parser = JavaParser()
    result = parser.parse(code, "test_file")

    assert len(result.imports) == 2
    imports = [i.module for i in result.imports]
    assert "java.util.List" in imports
    assert "java.util.Map" in imports


def test_parse_spring_endpoint():
    code = """
@RestController
@RequestMapping("/api")
public class UserController {
    
    @GetMapping("/users")
    public List<User> getUsers() {
        return userService.getAll();
    }
}
"""
    parser = JavaParser()
    result = parser.parse(code, "test_file")

    endpoint_symbols = [s for s in result.symbols if s.kind == "endpoint"]
    assert len(endpoint_symbols) == 1
    assert endpoint_symbols[0].name == "getUsers"
    assert endpoint_symbols[0].http_method == "GET"
