"""Tests for main CLI interface."""

from click.testing import CliRunner

from bydefault.cli import main


def test_cli_help(cli_runner: CliRunner) -> None:
    """Test CLI help output."""
    result = cli_runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "byDefault CLI tool" in result.output
    assert "merge" in result.output
    assert "version" in result.output


def test_cli_version_command(cli_runner):
    """Test version command is registered."""
    result = cli_runner.invoke(main, ["version", "--help"])
    assert result.exit_code == 0
    assert "Update version number" in result.output


def test_cli_merge_command(cli_runner):
    """Test merge command is registered."""
    result = cli_runner.invoke(main, ["merge", "--help"])
    assert result.exit_code == 0
    assert "Merge local configurations" in result.output
