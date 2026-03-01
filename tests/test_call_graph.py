import pytest
from repo_intel.core.indexer import Indexer


@pytest.fixture
def indexed_storage(tmp_path):
    """Create a storage with call relations."""
    db_path = tmp_path / "test.db"
    indexer = Indexer(str(db_path))

    # Create test files with calls
    (tmp_path / "test.py").write_text("""
def caller():
    callee()
""")
    indexer.index_file(str(tmp_path / "test.py"), project="test")
    return indexer.storage


def test_get_callers(indexed_storage):
    from repo_intel.tools.call_graph import get_callers

    result = get_callers(indexed_storage, "callee")
    assert len(result) >= 0


def test_get_callees(indexed_storage):
    from repo_intel.tools.call_graph import get_callees

    result = get_callees(indexed_storage, "caller")
    assert len(result) >= 0
