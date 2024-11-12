"""Tests for the main CLI interface."""

import pytest
from click.testing import CliRunner
from rich.console import Console


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_cli_version(cli_runner: CliRunner):
    """Test version flag shows correct version."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "bydefault, version" in result.output


def test_cli_help(cli_runner: CliRunner):
    """Test help text includes development status."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "under active development" in result.output
    assert "planned but not yet implemented" in result.output


def test_cli_verbose(cli_runner: CliRunner, mock_console: Console):
    """Test verbose flag enables additional output."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli, ["--verbose"])
    assert result.exit_code == 0
    assert "Verbose output enabled" in result.output


def test_cli_no_command(cli_runner: CliRunner):
    """Test root command shows development status."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli)
    assert result.exit_code == 0
    assert "Development Status" in result.output
    assert "under development" in result.output
