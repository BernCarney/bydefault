"""Tests for the validate command implementation."""

from textwrap import dedent

import pytest

from bydefault.commands.validator import validate_file
from bydefault.models.validation_results import IssueType


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


def test_validate_valid_props_conf(valid_props_conf):
    """Test validation of a valid props.conf file."""
    result = validate_file(valid_props_conf)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 1
    assert result.stats["lines"] > 0


def test_validate_valid_meta_conf(valid_meta_conf):
    """Test validation of a meta conf with empty section."""
    result = validate_file(valid_meta_conf)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 1


def test_validate_invalid_props_conf(invalid_props_conf):
    """Test validation catches syntax errors in props.conf."""
    result = validate_file(invalid_props_conf)
    assert not result.is_valid
    assert len(result.issues) > 0
    assert any(issue.type == IssueType.SYNTAX for issue in result.issues)


def test_validate_invalid_extension(temp_conf_dir):
    """Test validation fails for invalid file extension."""
    invalid_file = temp_conf_dir / "props.txt"
    invalid_file.write_text("[test]\nkey=value")

    result = validate_file(invalid_file)
    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].type == IssueType.STRUCTURE


def test_validate_empty_file(temp_conf_dir):
    """Test validation of an empty configuration file."""
    empty_file = temp_conf_dir / "empty.conf"
    empty_file.write_text("")

    result = validate_file(empty_file)
    assert result.is_valid
    assert not result.issues
    assert result.stats["lines"] == 0


def test_validate_duplicate_stanzas(temp_conf_dir):
    """Test validation catches duplicate stanzas."""
    content = dedent("""
        [test]
        key = value1
        
        [test]
        key = value2
    """).lstrip()

    file_path = temp_conf_dir / "duplicate.conf"
    file_path.write_text(content)

    result = validate_file(file_path)
    assert not result.is_valid
    assert any(issue.type == IssueType.DUPLICATE for issue in result.issues)


def test_validate_special_sections(temp_conf_dir):
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

    result = validate_file(file_path)
    assert result.is_valid
    assert not result.issues
    assert result.stats["stanzas"] == 3


def test_validate_non_utf8_file(temp_conf_dir):
    """Test validation of non-UTF8 encoded file."""
    file_path = temp_conf_dir / "invalid_encoding.conf"
    with open(file_path, "wb") as f:
        f.write(b"\xff\xfe invalid utf-8 content")

    result = validate_file(file_path)
    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].type == IssueType.ENCODING
