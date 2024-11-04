"""Tests for configuration file structures."""

from pathlib import Path

import pytest

from bydefault.core import ConfFile, ConfLine, ConfStanza, ConfValue


@pytest.fixture
def sample_conf_file(tmp_path: Path) -> Path:
    """Create a sample .conf file."""
    conf_path = tmp_path / "test.conf"
    conf_path.touch()
    return conf_path


def test_conf_value_creation():
    """Test ConfValue creation and properties."""
    value = ConfValue("test_value")
    assert value.value == "test_value"
    assert not value.is_continued


def test_conf_stanza_creation():
    """Test ConfStanza creation and validation."""
    # Valid stanza
    stanza = ConfStanza("[test]")
    assert stanza.name == "[test]"
    assert not stanza.settings

    # Invalid stanza format
    with pytest.raises(ValueError, match="Invalid stanza format"):
        ConfStanza("invalid")


def test_conf_stanza_is_default():
    """Test default stanza detection."""
    default_stanza = ConfStanza("[default]")
    other_stanza = ConfStanza("[test]")

    assert default_stanza.is_default_stanza
    assert not other_stanza.is_default_stanza


def test_conf_line_number_calculation():
    """Test line number calculation logic."""
    lines = [
        ConfLine(number=1),
        ConfLine(number=2),
        ConfLine(number=3),
    ]

    # Test end position (default)
    assert ConfLine.calculate_line_number(lines) == 4

    # Test start position
    assert ConfLine.calculate_line_number(lines, "start") == 1

    # Test empty lines list
    assert ConfLine.calculate_line_number([]) == 1

    # Test invalid position
    with pytest.raises(ValueError, match="Invalid position"):
        ConfLine.calculate_line_number(lines, "invalid")


def test_conf_file_creation(sample_conf_file: Path):
    """Test ConfFile creation and validation."""
    # Valid conf file
    conf_file = ConfFile(sample_conf_file)
    assert conf_file.path == sample_conf_file
    assert not conf_file.lines

    # Non-existent file
    with pytest.raises(FileNotFoundError):
        ConfFile(Path("nonexistent.conf"))

    # Invalid extension
    invalid_file = sample_conf_file.parent / "test.txt"
    invalid_file.touch()
    with pytest.raises(ValueError, match="Not a .conf file"):
        ConfFile(invalid_file)


def test_conf_file_add_line(sample_conf_file: Path):
    """Test adding lines to ConfFile."""
    conf_file = ConfFile(sample_conf_file)

    # Add regular line
    line1 = conf_file.add_line(1, content=ConfValue("test"))
    assert line1.number == 1

    # Add comment line (is_comment automatically set)
    line2 = conf_file.add_line(2, comment_text="# comment")
    assert line2.is_comment
    assert line2.comment_text == "# comment"

    # Add blank line
    line3 = conf_file.add_line(3, is_blank=True)
    assert line3.is_blank
    assert not line3.is_comment
    assert not line3.content

    # Test line number validation
    with pytest.raises(ValueError, match="Line numbers must be positive"):
        conf_file.add_line(0)

    with pytest.raises(ValueError, match="not sequential"):
        conf_file.add_line(1)  # Duplicate line number


def test_conf_file_add_setting_to_stanza(sample_conf_file: Path):
    """Test adding settings to stanzas in ConfFile."""
    conf_file = ConfFile(sample_conf_file)

    # Add stanza
    stanza = ConfStanza("[test]")
    conf_file.add_line(1, stanza)

    # Add setting (default end position)
    conf_file.add_setting_to_stanza("[test]", "key1", "value1")
    assert len(conf_file.lines) == 2
    assert isinstance(conf_file.lines[1].content, ConfValue)

    # Add setting at start
    conf_file.add_setting_to_stanza("[test]", "key2", "value2", position="start")
    assert len(conf_file.lines) == 3

    # Test invalid stanza
    with pytest.raises(ValueError, match="Stanza not found"):
        conf_file.add_setting_to_stanza("[nonexistent]", "key", "value")


def test_conf_file_stanza_property(sample_conf_file: Path):
    """Test stanzas property of ConfFile."""
    conf_file = ConfFile(sample_conf_file)

    # Add multiple stanzas
    stanza1 = ConfStanza("[test1]")
    stanza2 = ConfStanza("[test2]")

    conf_file.add_line(1, stanza1)
    conf_file.add_line(2, ConfValue("value1"))
    conf_file.add_line(3, stanza2)
    conf_file.add_line(4, ConfValue("value2"))

    stanzas = conf_file.stanzas
    assert len(stanzas) == 2
    assert stanzas[0].name == "[test1]"
    assert stanzas[1].name == "[test2]"
