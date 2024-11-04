"""Tests for configuration value parser."""

from bydefault.core import ConfValueParser


def test_parse_simple_value():
    """Test parsing a simple value without continuations."""
    result = ConfValueParser.parse("simple value")
    assert result.value == "simple value"
    assert not result.continuation_lines
    assert not result.inline_comment


def test_parse_value_with_inline_comment():
    """Test parsing a value with an inline comment."""
    result = ConfValueParser.parse("value # comment")
    assert result.value == "value"
    assert result.inline_comment == "comment"


def test_parse_value_with_continuation():
    """Test parsing a value with continuation lines."""
    result = ConfValueParser.parse(
        "first line \\",
        ["    second line", "    third line"],
    )
    assert result.value == "first line second line third line"
    assert len(result.continuation_lines) == 2
    assert result.continuation_lines[0] == "    second line"


def test_parse_value_with_continuation_and_comments():
    """Test parsing a value with both continuations and comments."""
    result = ConfValueParser.parse(
        "first line \\ # comment 1",
        ["    second line \\ # comment 2", "    third line # final comment"],
    )
    assert result.value == "first line second line third line"
    assert result.inline_comment == "final comment"
    assert len(result.continuation_lines) == 2


def test_parse_empty_value():
    """Test parsing an empty value."""
    result = ConfValueParser.parse("")
    assert result.value == ""
    assert not result.continuation_lines
    assert not result.inline_comment


def test_parse_escaped_backslash():
    """Test parsing a value with escaped backslash."""
    result = ConfValueParser.parse("value with \\\\ backslash")
    assert result.value == "value with \\ backslash"
    assert not result.continuation_lines
