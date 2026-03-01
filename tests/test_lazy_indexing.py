import pytest
import tempfile
import time
from pathlib import Path
from repo_intel.core.storage import Storage
from repo_intel.core.indexer import Indexer
from repo_intel.core.config import Config, get_config


def test_stale_detection_empty_db():
    """Test that empty DB is considered stale."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / ".repo-intel" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        storage = Storage(str(db_path))

        # Empty DB should be stale
        assert storage.is_index_stale(tmpdir) is True


def test_stale_detection_fresh_index():
    """Test that fresh index is not stale."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / ".repo-intel" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        storage = Storage(str(db_path))

        # Create a file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Index the project
        indexer = Indexer(str(db_path), verbose=False)
        indexer.index_project(tmpdir, "test")

        # Should not be stale immediately after indexing
        storage2 = Storage(str(db_path))
        assert storage2.is_index_stale(tmpdir) is False


def test_stale_detection_old_index():
    """Test that old index is considered stale."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / ".repo-intel" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        storage = Storage(str(db_path))

        # Create a file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Index the project
        indexer = Indexer(str(db_path), verbose=False)
        indexer.index_project(tmpdir, "test")

        # Set last index time to 2 hours ago
        storage2 = Storage(str(db_path))
        storage2.set_last_index_time(time.time() - 7200)

        # Should be stale now
        assert storage2.is_index_stale(tmpdir) is True


def test_stale_detection_file_count_mismatch():
    """Test that file count mismatch causes staleness."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / ".repo-intel" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        storage = Storage(str(db_path))

        # Create initial file
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Index the project
        indexer = Indexer(str(db_path), verbose=False)
        indexer.index_project(tmpdir, "test")

        # Add many new files (more than variance threshold of 5)
        for i in range(10):
            new_file = Path(tmpdir) / f"new{i}.py"
            new_file.write_text("def func():\n    pass\n")

        # Should be stale due to file count mismatch
        storage2 = Storage(str(db_path))
        assert storage2.is_index_stale(tmpdir) is True


def test_last_index_time_persistence():
    """Test that last index time persists across Storage instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / ".repo-intel" / "test.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        storage1 = Storage(str(db_path))

        # Set last index time
        test_time = 1234567890.0
        storage1.set_last_index_time(test_time)

        # Create new storage instance
        storage2 = Storage(str(db_path))

        # Should retrieve the same time
        assert storage2.get_last_index_time() == test_time
