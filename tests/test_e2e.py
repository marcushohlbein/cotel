import pytest
from pathlib import Path
from repo_intel.core.indexer import Indexer
from repo_intel.core.storage import Storage
from repo_intel.tools.list_symbols import list_symbols
from repo_intel.tools.find_symbol import find_symbol


def test_full_indexing_workflow(tmp_path):
    # Create test project
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("""
def greet(name):
    return f"Hello, {name}"

def main():
    greet("World")
""")

    # Index project
    db_path = tmp_path / "index.db"
    indexer = Indexer(str(db_path))
    result = indexer.index_project(str(tmp_path), project="test")

    assert result.indexed >= 1

    # Query symbols
    storage = Storage(str(db_path))
    symbols = list_symbols(storage)

    assert len(symbols) >= 2
    symbol_names = [s["name"] for s in symbols]
    assert "greet" in symbol_names
    assert "main" in symbol_names

    # Find specific symbol
    greet_symbol = find_symbol(storage, "greet")
    assert greet_symbol is not None
    assert greet_symbol["kind"] == "function"
