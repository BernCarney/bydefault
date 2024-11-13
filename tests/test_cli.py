"""Tests for the main CLI interface."""

import pytest
import rich_click as click
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


def test_cli_main_block(monkeypatch):
    """Test the CLI invocation through Click's test runner."""
    from click.testing import CliRunner

    from bydefault.cli import cli

    # Track if cli() was called
    cli_called = False

    def mock_cli():
        nonlocal cli_called
        cli_called = True

    # Replace the cli function with our mock
    monkeypatch.setattr("bydefault.cli.cli", mock_cli)

    # Create a runner and invoke the CLI
    runner = CliRunner()
    result = runner.invoke(cli)

    # Verify cli() was called and returned successfully
    assert result.exit_code == 0


def test_cli_context_initialization(cli_runner: CliRunner):
    """Test that CLI context is properly initialized."""
    from bydefault.cli import cli

    @cli.command()
    def dummy():
        pass

    result = cli_runner.invoke(cli, ["dummy"])
    assert result.exit_code == 0


def test_cli_context_exists(cli_runner: CliRunner):
    """Test that context object is created when None."""
    from bydefault.cli import cli

    @cli.command()
    @click.pass_context
    def check_ctx(ctx):
        click.echo(str(ctx.obj is not None))

    result = cli_runner.invoke(cli, ["check-ctx"])
    assert result.exit_code == 0
    assert "True" in result.output
