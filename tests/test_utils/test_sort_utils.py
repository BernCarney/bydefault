"""Tests for the sort utilities."""

import pytest

from bydefault.utils.sort_utils import ConfigSorter


@pytest.fixture
def test_conf_content():
    """Return test configuration content."""
    return """# Global comment
setting1 = value1
setting2 = value2

[default]
# Default stanza comment
default_setting2 = value2
default_setting1 = value1

[type::*]
# Wildcard stanza comment
wildcard_setting2 = value2
wildcard_setting1 = value1

[type::specific]
# Specific stanza comment
specific_setting2 = value2
specific_setting1 = value1
"""


@pytest.fixture
def test_conf_file(tmp_path, test_conf_content):
    """Create a test configuration file."""
    file_path = tmp_path / "test.conf"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_conf_content)
    return file_path


def test_config_sorter_init(test_conf_file):
    """Test ConfigSorter initialization."""
    sorter = ConfigSorter(test_conf_file)
    assert sorter.file_path == test_conf_file
    assert sorter.verbose is False


def test_config_sorter_parse(test_conf_file):
    """Test ConfigSorter parse method."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    # We'll need to check the parsed structure once implemented


def test_config_sorter_sort(test_conf_file):
    """Test ConfigSorter sort method."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    result = sorter.sort()

    # Once implemented, we should check:
    # - Stanzas are ordered correctly (default, wildcard, specific)
    # - Settings are sorted alphabetically
    # - Comments are preserved
    assert isinstance(result, dict)
    assert "stanzas_reordered" in result
    assert "settings_sorted" in result
    assert "comments_preserved" in result


def test_config_sorter_write(test_conf_file):
    """Test ConfigSorter write method."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    sorter.sort()

    # Capture the file content before writing
    with open(test_conf_file, "r", encoding="utf-8") as f:
        before_content = f.read()

    # Write the sorted content
    sorter.write()

    # Read the file content after writing
    with open(test_conf_file, "r", encoding="utf-8") as f:
        after_content = f.read()

    # The content should be different after sorting
    # (once writing is implemented)
    assert isinstance(after_content, str)


def test_config_sorter_preserve_comments(test_conf_file):
    """Test that comments are preserved during sorting."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    sorter.sort()
    sorter.write()

    # Read the file content after writing
    with open(test_conf_file, "r", encoding="utf-8") as f:
        after_content = f.read()

    # Check that all comments are present in the sorted file
    assert "# Global comment" in after_content
    assert "# Default stanza comment" in after_content
    assert "# Wildcard stanza comment" in after_content
    assert "# Specific stanza comment" in after_content


def test_config_sorter_stanza_order(test_conf_file):
    """Test that stanzas are ordered correctly."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    sorter.sort()
    sorter.write()

    # Read the file content after writing
    with open(test_conf_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract stanza lines
    stanza_lines = [line.strip() for line in lines if line.strip().startswith("[")]

    # Check that stanzas are in the correct order:
    # 1. Global settings (not a stanza)
    # 2. Default stanza
    # 3. Global wildcard stanzas
    # 4. Type-specific stanzas
    assert stanza_lines[0] == "[default]"
    assert stanza_lines[1] == "[type::*]"
    assert stanza_lines[2] == "[type::specific]"


def test_config_sorter_settings_sorted(test_conf_file):
    """Test that settings are sorted alphabetically within stanzas."""
    sorter = ConfigSorter(test_conf_file)
    sorter.parse()
    sorter.sort()
    sorter.write()

    # Read the file content after writing
    with open(test_conf_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that settings are in alphabetical order within stanzas
    # This requires parsing the file and checking each stanza's settings

    # For now, we'll do a simple check that setting1 appears before setting2
    # in each stanza section
    default_section = content.split("[default]")[1].split("[")[0]
    assert default_section.find("default_setting1") < default_section.find(
        "default_setting2"
    )

    wildcard_section = content.split("[type::*]")[1].split("[")[0]
    assert wildcard_section.find("wildcard_setting1") < wildcard_section.find(
        "wildcard_setting2"
    )

    specific_section = content.split("[type::specific]")[1]
    assert specific_section.find("specific_setting1") < specific_section.find(
        "specific_setting2"
    )
