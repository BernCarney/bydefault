"""Tests for output formatting utilities."""

from rich.console import Console
from rich.theme import Theme

from bydefault.utils.output import create_console, format_error


def test_create_console():
    """Test console creation with proper theme."""
    console = create_console()
    assert isinstance(console, Console)
    assert isinstance(console.theme, Theme)

    # Verify required theme styles are present
    assert "info" in console.theme.styles
    assert "warning" in console.theme.styles
    assert "error" in console.theme.styles
    assert "success" in console.theme.styles


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


def test_theme_colors():
    """Test theme color configuration."""
    console = create_console()
    theme = console.theme

    assert theme.styles["info"].color == "cyan"
    assert theme.styles["warning"].color == "yellow"
    assert theme.styles["error"].color == "red"
    assert theme.styles["success"].color == "green"

    # Verify error style includes bold
    assert theme.styles["error"].bold is True
