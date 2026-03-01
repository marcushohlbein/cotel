import pytest
from repo_intel.core.indexer import Indexer


@pytest.fixture
def indexed_storage(tmp_path):
    """Create a storage with some indexed data."""
    db_path = tmp_path / "test.db"
    indexer = Indexer(str(db_path))

    # Create test files
    (tmp_path / "test.py").write_text("""
def hello():
    pass

class MyClass:
    def method(self):
        hello()
""")

    indexer.index_file(str(tmp_path / "test.py"), project="test")
    return indexer.storage


def test_list_symbols(indexed_storage):
    from repo_intel.tools.list_symbols import list_symbols

    result = list_symbols(indexed_storage)
    assert len(result) > 0
    assert "name" in result[0]
    assert "kind" in result[0]


def test_list_symbols_filter_by_kind(indexed_storage):
    from repo_intel.tools.list_symbols import list_symbols

    result = list_symbols(indexed_storage, kind_filter="function")
    for symbol in result:
        assert symbol["kind"] == "function"
