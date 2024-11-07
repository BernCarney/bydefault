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


def test_parser_escaped_backslash():
    """Test parsing value with escaped backslashes."""
    result = ConfValueParser.parse(r"path=C:\\Program Files\\Splunk")
    assert result.value == r"path=C:\Program Files\Splunk"
    assert not result.continuation_lines


def test_parser_multiple_continuations_with_comments():
    """Test parsing multiple continuation lines with comments."""
    result = ConfValueParser.parse(
        "first \\ # comment1", ["    second \\ # comment2", "    third # final comment"]
    )
    assert result.value == "first second third"
    assert result.inline_comment == "final comment"
    assert len(result.continuation_lines) == 2


def test_parser_empty_continuation():
    """Test parsing empty continuation lines."""
    result = ConfValueParser.parse("value \\", ["    ", "    next"])
    assert result.value == "value next"
    assert len(result.continuation_lines) == 2


def test_parser_only_comment():
    """Test parsing line with only comment."""
    result = ConfValueParser.parse("# comment")
    assert result.value == ""
    assert result.inline_comment == "comment"


def test_parse_empty_value_with_comment():
    """Test parsing empty value with comment."""
    result = ConfValueParser.parse("# comment")
    assert result.value == ""
    assert result.inline_comment == "comment"


def test_parse_multiple_escaped_backslashes():
    """Test parsing value with multiple escaped backslashes."""
    result = ConfValueParser.parse(r"value\\\\value")
    assert result.value == r"value\\value"


def test_parse_continuation_with_multiple_spaces():
    """Test parsing continuation with varying whitespace."""
    result = ConfValueParser.parse("value1    \\", ["    value2    "])
    assert result.value == "value1 value2"
