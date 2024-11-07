"""Tests for main CLI interface."""

import pytest
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


def test_merge_command_exists(cli_runner):
    """Test that the merge command exists and shows help."""
    result = cli_runner.invoke(main, ["merge", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

@pytest.mark.skip(reason="Merge functionality not yet implemented")
def test_merge_command_with_invalid_path(cli_runner):
    """Test merge command with invalid path."""
    pass
