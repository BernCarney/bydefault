"""Tests for the validate command implementation."""

from textwrap import dedent
from unittest.mock import Mock

import pytest
from rich.console import Console

from bydefault.commands.validator import (
    _get_unique_section_name,
    _is_splunk_special_section,
    _read_file_content,
    _validate_encoding,
    _validate_file_extension,
    _validate_stanzas,
    validate_file,
)
from bydefault.models.validation_results import IssueType


@pytest.fixture
def mock_console():
    """Create a mock console for testing verbose output."""
    return Mock(spec=Console)


@pytest.fixture
def temp_conf_dir(tmp_path):
    """Create a temporary directory with test configuration files."""
    conf_dir = tmp_path / "conf"
    conf_dir.mkdir()
    return conf_dir


@pytest.fixture
def valid_props_conf(temp_conf_dir):
    """Create a valid props.conf file."""
    content = dedent("""
        [source::test_logs]
        SHOULD_LINEMERGE = false
        LINE_BREAKER = ([\\r\\n]+)
        TRANSFORMS-test = test_transform
    """).lstrip()

    file_path = temp_conf_dir / "props.conf"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def valid_meta_conf(temp_conf_dir):
    """Create a valid meta file with empty section."""
    content = dedent("""
        []
        access = read : [ * ], write : [ admin ]
        export = system
    """).lstrip()

    file_path = temp_conf_dir / "default.meta"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def invalid_props_conf(temp_conf_dir):
    """Create an invalid props.conf with various errors."""
    content = dedent("""
        # Missing closing bracket
        [source::bad_stanza
        SHOULD_LINEMERGE = false

        # Duplicate stanza
        [source::duplicate]
        key = value1

        [source::duplicate]
        key = value2

        # Invalid key format
        [source::invalid_keys]
        BAD KEY = value
    """).lstrip()

    file_path = temp_conf_dir / "invalid_props.conf"
    file_path.write_text(content)
    return file_path


def test_is_splunk_special_section():
    """Test special section detection."""
    assert _is_splunk_special_section("[]")
    assert _is_splunk_special_section("[*]")
    assert _is_splunk_special_section("[default]")
    assert not _is_splunk_special_section("[regular]")


def test_get_unique_section_name():
    """Test special section name conversion."""
    assert _get_unique_section_name("[]") == "global_default"
    assert _get_unique_section_name("[*]") == "wildcard"
    assert _get_unique_section_name("[default]") == "explicit_default"
    assert _get_unique_section_name("[regular]") == "regular"


def test_validate_file_extension(temp_conf_dir, mock_console):
    """Test file extension validation."""
    valid_file = temp_conf_dir / "test.conf"
    valid_file.touch()
    invalid_file = temp_conf_dir / "test.txt"
    invalid_file.touch()

    # Test valid extension
    is_valid, issues = _validate_file_extension(valid_file, True, mock_console)
    assert is_valid
    assert not issues
    mock_console.print.assert_called()

    # Test invalid extension
    is_valid, issues = _validate_file_extension(invalid_file, True, mock_console)
    assert not is_valid
    assert len(issues) == 1
    assert issues[0].type == IssueType.STRUCTURE


def test_validate_encoding(temp_conf_dir, mock_console):
    """Test file encoding validation."""
    valid_file = temp_conf_dir / "valid.conf"
    valid_file.write_text("test", encoding="utf-8")

    invalid_file = temp_conf_dir / "invalid.conf"
    with open(invalid_file, "wb") as f:
        f.write(b"\xff\xfe invalid utf-8")

    # Test valid encoding
    is_valid, issues = _validate_encoding(valid_file, True, mock_console)
    assert is_valid
    assert not issues
    mock_console.print.assert_called()

    # Test invalid encoding
    is_valid, issues = _validate_encoding(invalid_file, True, mock_console)
    assert not is_valid
    assert len(issues) == 1
    assert issues[0].type == IssueType.ENCODING


def test_read_file_content(temp_conf_dir, mock_console):
    """Test file content reading."""
    test_file = temp_conf_dir / "test.conf"
    content = dedent("""
        [test]
        key = value
    """).lstrip()
    test_file.write_text(content)

    content, stats = _read_file_content(test_file, True, mock_console)
    assert len(content) == 2
    assert stats["lines"] == 2
    mock_console.print.assert_called()


def test_validate_stanzas(mock_console):
    """Test stanza validation."""
    content = (
        dedent("""
        [valid]
        key = value

        [duplicate]
        key = value1

        [duplicate]
        key = value2

        [unclosed
        key = value
    """)
        .lstrip()
        .splitlines()
    )

    seen_sections, issues = _validate_stanzas(content, True, mock_console)
    assert len(issues) == 2
    assert any(i.type == IssueType.DUPLICATE for i in issues)
    assert any(i.type == IssueType.SYNTAX for i in issues)
    mock_console.print.assert_called()


def test_validate_file_verbose(temp_conf_dir, mock_console):
    """Test verbose output during validation."""
    test_file = temp_conf_dir / "test.conf"
    content = dedent("""
        [test]
        key = value
    """).lstrip()
    test_file.write_text(content)

    result = validate_file(test_file, verbose=True, console=mock_console)
    assert result.is_valid
    assert mock_console.print.called
    # Check that console.print was called for each validation step
    assert mock_console.print.call_count >= 4


def test_validate_valid_props_conf(valid_props_conf, mock_console):
    """Test validation of a valid props.conf file."""
    result = validate_file(valid_props_conf, verbose=False, console=mock_console)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 1
    assert result.stats["lines"] > 0


def test_validate_valid_meta_conf(valid_meta_conf, mock_console):
    """Test validation of a meta conf with empty section."""
    result = validate_file(valid_meta_conf, verbose=False, console=mock_console)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 1


def test_validate_invalid_props_conf(invalid_props_conf, mock_console):
    """Test validation catches syntax errors in props.conf."""
    result = validate_file(invalid_props_conf, verbose=False, console=mock_console)
    assert not result.is_valid
    assert len(result.issues) > 0
    assert any(issue.type == IssueType.SYNTAX for issue in result.issues)


def test_validate_invalid_extension(temp_conf_dir, mock_console):
    """Test validation fails for invalid file extension."""
    invalid_file = temp_conf_dir / "props.txt"
    invalid_file.write_text("[test]\nkey=value")

    result = validate_file(invalid_file, verbose=False, console=mock_console)
    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].type == IssueType.STRUCTURE


def test_validate_empty_file(temp_conf_dir, mock_console):
    """Test validation of an empty configuration file."""
    empty_file = temp_conf_dir / "empty.conf"
    empty_file.write_text("")

    result = validate_file(empty_file, verbose=False, console=mock_console)
    assert result.is_valid
    assert not result.issues
    assert result.stats["lines"] == 0


def test_validate_duplicate_stanzas(temp_conf_dir, mock_console):
    """Test validation catches duplicate stanzas."""
    content = dedent("""
        [test]
        key = value1
        
        [test]
        key = value2
    """).lstrip()

    file_path = temp_conf_dir / "duplicate.conf"
    file_path.write_text(content)

    result = validate_file(file_path, verbose=False, console=mock_console)
    assert not result.is_valid
    assert any(issue.type == IssueType.DUPLICATE for issue in result.issues)


def test_validate_special_sections(temp_conf_dir, mock_console):
    """Test validation of Splunk special sections."""
    content = dedent("""
        []
        key1 = value1
        
        [*]
        key2 = value2
        
        [default]
        key3 = value3
    """).lstrip()

    file_path = temp_conf_dir / "special.conf"
    file_path.write_text(content)

    result = validate_file(file_path, verbose=False, console=mock_console)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 3


def test_validate_non_utf8_file(temp_conf_dir, mock_console):
    """Test validation of non-UTF8 encoded file."""
    file_path = temp_conf_dir / "invalid_encoding.conf"
    with open(file_path, "wb") as f:
        f.write(b"\xff\xfe invalid utf-8 content")

    result = validate_file(file_path, verbose=False, console=mock_console)
    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].type == IssueType.ENCODING
