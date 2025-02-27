"""Tests for command initialization."""

from bydefault.commands import __all__


def test_commands_all_empty():
    """Test that __all__ is initialized with the expected commands."""
    assert isinstance(__all__, list)
    assert len(__all__) == 3  # validator, scan, and sort commands
