def test_toon_formatter_exists():
    """Test that TOONFormatter class exists"""
    from repo_intel.formatters.toon_formatter import TOONFormatter

    formatter = TOONFormatter()
    assert hasattr(formatter, "format")


def test_toon_formatter_output():
    """Test that TOON formatter produces valid output"""
    from repo_intel.formatters.toon_formatter import TOONFormatter

    formatter = TOONFormatter()

    symbols = [
        {
            "name": "foo",
            "kind": "function",
            "file": "a.py",
            "start_line": 10,
            "end_line": 20,
            "signature": "def foo(x, y)",
        },
        {
            "name": "Bar",
            "kind": "class",
            "file": "b.py",
            "start_line": 5,
            "end_line": 30,
            "signature": "class Bar:",
        },
    ]

    files = [
        {"path": "a.py", "symbol_count": 5, "language": "python"},
        {"path": "b.py", "symbol_count": 3, "language": "python"},
    ]

    metadata = {"project": "test", "tokens_used": 50}

    output = formatter.format(symbols, files, metadata)

    # Check structure
    assert "repo_map{" in output
    assert "symbols[2]" in output
    assert "files[2]" in output

    # Check content
    assert "foo" in output
    assert "Bar" in output
    assert "a.py" in output
    assert "b.py" in output
