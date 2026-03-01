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
""")

    indexer.index_file(str(tmp_path / "test.py"), project="test")
    return indexer.storage


def test_find_symbol_by_name(indexed_storage):
    from repo_intel.tools.find_symbol import find_symbol

    result = find_symbol(indexed_storage, "hello")
    assert result is not None
    assert result["name"] == "hello"


def test_find_symbol_not_found(indexed_storage):
    from repo_intel.tools.find_symbol import find_symbol

    result = find_symbol(indexed_storage, "nonexistent")
    assert result is None
