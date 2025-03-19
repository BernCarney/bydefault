"""Tests for the commands module."""

from bydefault.commands import __all__


def test_commands_all_empty():
    """Test that __all__ is initialized with the expected commands."""
    assert isinstance(__all__, list)
    assert len(__all__) == 4  # validator, scan, sort, and merge commands
    assert "validator" in __all__
    assert "scan" in __all__
    assert "sort" in __all__
    assert "merge" in __all__
