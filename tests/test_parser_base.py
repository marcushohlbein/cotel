from repo_intel.parsers.base import Parser, ParseResult


def test_parse_result_structure():
    result = ParseResult(symbols=[], relations=[])
    assert result.symbols == []
    assert result.relations == []


def test_parser_interface():
    class TestParser(Parser):
        def parse(self, content: str, file_id: str) -> ParseResult:
            return ParseResult(symbols=[], relations=[])

    parser = TestParser()
    result = parser.parse("test content", "file_id")
    assert isinstance(result, ParseResult)


def test_parser_extract_references():
    """Test that parser has extract_references method"""

    class TestParser(Parser):
        def parse(self, content: str, file_id: str) -> ParseResult:
            return ParseResult(symbols=[], relations=[])

    parser = TestParser()

    # Should have method
    assert hasattr(parser, "extract_references")

    # Should return list
    code = "def foo(): pass\nbar()"
    refs = parser.extract_references(code)
    assert isinstance(refs, list)
