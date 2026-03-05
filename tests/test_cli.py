def test_cli_default_command():
    """Test that CLI has default repomap command"""
    from click.testing import CliRunner
    from repo_intel.cli import cli

    runner = CliRunner()

    # Should have default command
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "repomap" in result.output.lower() or "generate" in result.output.lower()
