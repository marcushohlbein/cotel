import pytest
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage


@pytest.fixture
def temp_indexer(tmp_path):
    db_path = tmp_path / "test.db"
    return Indexer(str(db_path))


def test_index_file(temp_indexer, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def hello():
    pass
""")

    temp_indexer.index_file(str(test_file), project="test")

    symbols = temp_indexer.storage.get_symbols()
    assert len(symbols) == 1
    assert symbols[0].name == "hello"


def test_index_project(temp_indexer, tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def func1(): pass")
    (tmp_path / "src" / "utils.py").write_text("def func2(): pass")

    temp_indexer.index_project(str(tmp_path), project="test")

    symbols = temp_indexer.storage.get_symbols()
    assert len(symbols) >= 2


def test_indexer_stores_references(temp_indexer, tmp_path):
    """Test that indexer stores symbol references"""
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def helper():
    pass

def main():
    helper()
""")

    # Index
    temp_indexer.index_file(str(test_file), project="test")

    # Check references were stored
    cursor = temp_indexer.storage.conn.execute('SELECT COUNT(*) FROM "references"')
    count = cursor.fetchone()[0]

    assert count > 0, "Should have stored references"
