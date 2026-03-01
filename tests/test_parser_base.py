from repo_intel.parsers.base import Parser, ParseResult


def test_parse_result_structure():
    result = ParseResult(symbols=[], imports=[], relations=[])
    assert result.symbols == []
    assert result.imports == []
    assert result.relations == []


def test_parser_interface():
    class TestParser(Parser):
        def parse(self, content: str, file_id: str) -> ParseResult:
            return ParseResult(symbols=[], imports=[], relations=[])

    parser = TestParser()
    result = parser.parse("test content", "file_id")
    assert isinstance(result, ParseResult)
