"""Tests for the main CLI interface."""

import pytest
from click.testing import CliRunner

from bydefault import __prog_name__, __version__


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_cli_version(cli_runner: CliRunner):
    """Test version flag shows correct version."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert f"{__prog_name__}, version {__version__}" in result.output.strip()


def test_cli_help(cli_runner: CliRunner):
    """Test help text includes development status."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "under active development" in result.output
    assert "CLI tools for Splunk TA development" in result.output


def test_cli_no_command(cli_runner: CliRunner):
    """Test root command shows help text."""
    from bydefault.cli import cli

    result = cli_runner.invoke(cli)
    assert result.exit_code == 0
    # Verify key elements of default output
    assert "Usage:" in result.output
    assert "CLI tools for Splunk TA development" in result.output
    assert "under active development" in result.output
    assert "--help" in result.output
    assert "--version" in result.output
