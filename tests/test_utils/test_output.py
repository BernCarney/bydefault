"""Tests for output formatting utilities."""

import rich_click as click
from click.testing import CliRunner

from bydefault.utils.output import (
    CHALKY,
    CORAL,
    CYAN,
    IVORY,
    MALIBU,
    SAGE,
    STONE,
    format_error,
)


def test_rich_click_styling():
    """Test rich-click styling configuration."""
    # Basic configuration
    assert click.rich_click.USE_RICH_MARKUP is True
    assert click.rich_click.USE_MARKDOWN is True

    # Command and options styling
    assert click.rich_click.STYLE_COMMAND == f"bold {MALIBU}"
    assert click.rich_click.STYLE_OPTION == f"bold {CYAN}"
    assert click.rich_click.STYLE_SWITCH == f"bold {SAGE}"
    assert click.rich_click.STYLE_METAVAR == CHALKY
    assert click.rich_click.STYLE_METAVAR_SEPARATOR == STONE

    # Help text styling
    assert click.rich_click.STYLE_HELPTEXT == IVORY
    assert click.rich_click.STYLE_HEADER_TEXT == f"bold {IVORY}"

    # Error styling
    assert click.rich_click.STYLE_ERRORS_MESSAGE == f"bold {CORAL}"
    assert click.rich_click.STYLE_ERRORS_SUGGESTION == STONE
    assert click.rich_click.STYLE_ERRORS_CMD == MALIBU


def test_styled_output(cli_runner: CliRunner):
    """Test that styled output appears in CLI."""
    from bydefault.cli import cli

    # Test help output contains styled elements
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0

    # Help text should contain styled elements
    assert "Options" in result.output  # Header should be bold ivory
    assert "--help" in result.output  # Option should be bold cyan
    assert "--version" in result.output  # Option should be bold cyan


def test_styled_error_output(cli_runner: CliRunner):
    """Test that error output is properly styled."""
    from bydefault.cli import cli

    # Test invalid command
    result = cli_runner.invoke(cli, ["invalid"])
    assert result.exit_code != 0

    # Error message should be styled
    assert "Error" in result.output  # Should be bold coral
    assert "invalid" in result.output  # Command should be light blue


def test_format_error_basic():
    """Test basic error message formatting."""
    message = "Something went wrong"
    formatted = format_error(message)
    assert formatted == "Error: Something went wrong"


def test_format_error_with_context():
    """Test error message formatting with context."""
    message = "File not found"
    context = "Check the path and try again"
    formatted = format_error(message, context)
    assert formatted == "Error: File not found\n  Check the path and try again"
