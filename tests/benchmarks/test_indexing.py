import pytest
from pathlib import Path
from repo_intel.core.indexer import Indexer


def test_indexing_performance_small(tmp_path):
    """Test indexing of small project (~100 LOC)."""
    # Create 10 Python files with ~10 LOC each
    for i in range(10):
        (tmp_path / f"file_{i}.py").write_text(f"""
def function_{i}():
    result = {i} * 2
    return result

def helper_{i}():
    function_{i}()
""")

    db_path = tmp_path / "bench.db"
    indexer = Indexer(str(db_path))

    import time

    start = time.time()
    indexed = indexer.index_project(str(tmp_path), project="bench")
    duration = time.time() - start

    assert indexed == 10
    assert duration < 2.0  # Should complete in under 2 seconds
