import pytest
import time
import tempfile
import threading
from pathlib import Path
from repo_intel.cli import main
from click.testing import CliRunner


def test_watch_command_starts():
    """Test that watch command starts without errors."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize repo-intel in temp directory
        result = runner.invoke(main, ["init", tmpdir])
        assert result.exit_code == 0

        # Create a Python file before watching
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Run watch in a thread (it will block)
        def run_watch():
            runner.invoke(main, ["watch", "--project", "test"], obj={"project_root": tmpdir})

        watch_thread = threading.Thread(target=run_watch, daemon=True)
        watch_thread.start()

        # Give it a moment to start
        time.sleep(1)

        # Thread should be running
        assert watch_thread.is_alive()

        # Thread will exit when test ends (daemon=True)


def test_watch_help():
    """Test watch command help output."""
    runner = CliRunner()
    result = runner.invoke(main, ["watch", "--help"])
    assert result.exit_code == 0
    assert "Watch for file changes" in result.output
    assert "--debounce" in result.output
    assert "--project" in result.output
