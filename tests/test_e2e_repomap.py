def test_e2e_repomap_generation():
    """Test complete repomap generation workflow"""
    import tempfile
    import os
    from pathlib import Path
    from click.testing import CliRunner
    from repo_intel.cli import cli

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save current directory
        orig_dir = os.getcwd()
        try:
            # Change to temp directory
            os.chdir(tmpdir)

            # Create sample Python project
            repo = Path(tmpdir)

            (repo / "main.py").write_text("""
from utils import helper

def main():
    helper()
    print("done")

if __name__ == '__main__':
    main()
""")

            (repo / "utils.py").write_text("""
def helper():
    return "helping"
""")

            # Initialize git repo
            import subprocess

            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "config", "user.name", "Test"], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "init"], check=True, capture_output=True)

            # Run repomap
            runner = CliRunner()
            result = runner.invoke(cli, ["--max-tokens", "500"])

            # Should succeed
            assert result.exit_code == 0

            # Should contain TOON format
            assert "repo_map{" in result.output
            assert "symbols[" in result.output

            # Should contain our functions
            assert "main" in result.output or "helper" in result.output
        finally:
            # Restore original directory
            os.chdir(orig_dir)
