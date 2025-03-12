"""Tests for the sort command."""

import os

import pytest
from click.testing import CliRunner

from bydefault.cli import cli


@pytest.fixture
def cli_runner():
    """Provide a Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def test_conf_file(tmp_path):
    """Create a test configuration file."""
    file_path = tmp_path / "test.conf"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(
            """# Global comment
setting1 = value1
setting2 = value2

[default]
# Default stanza comment
default_setting1 = value1
default_setting2 = value2

[type::*]
# Wildcard stanza comment
wildcard_setting1 = value1
wildcard_setting2 = value2

[type::specific]
# Specific stanza comment
specific_setting1 = value1
specific_setting2 = value2
"""
        )
    return file_path


@pytest.fixture
def multiple_global_stanza_file(tmp_path):
    """Create a test configuration file with multiple global stanza types."""
    file_path = tmp_path / "multiple_global.conf"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(
            """# Global settings outside any stanza
global_setting1 = value1
global_setting2 = value2

# Empty stanza
[]
empty_setting1 = value1
empty_setting2 = value2

# Star stanza
[*]
star_setting1 = value1
star_setting2 = value2

[default]
# Default stanza comment
default_setting1 = value1
default_setting2 = value2

[perfmon]
# App-specific stanza
interval = 60
disabled = 0

[source::example]
# Source-specific stanza
SHOULD_LINEMERGE = false
TRUNCATE = 10000
"""
        )
    return file_path


def test_sort_command_basic(cli_runner, test_conf_file):
    """Test basic sorting functionality."""
    result = cli_runner.invoke(cli, ["sort", str(test_conf_file)])
    assert result.exit_code == 0
    assert "Sorted:" in result.output


def test_sort_command_dry_run(cli_runner, test_conf_file):
    """Test dry run mode."""
    result = cli_runner.invoke(cli, ["sort", "--dry-run", str(test_conf_file)])
    assert result.exit_code == 0
    assert "Dry run: No changes made to" in result.output


def test_sort_command_backup(cli_runner, test_conf_file):
    """Test backup functionality."""
    result = cli_runner.invoke(cli, ["sort", "--backup", str(test_conf_file)])
    assert result.exit_code == 0
    assert "Created backup:" in result.output
    # Check that backup file exists
    backup_file = str(test_conf_file) + ".bak"
    assert os.path.exists(backup_file)


def test_sort_command_verbose(cli_runner, test_conf_file):
    """Test verbose output."""
    result = cli_runner.invoke(cli, ["sort", "--verbose", str(test_conf_file)])
    assert result.exit_code == 0
    # Detailed output should contain more information about sorting results
    assert "Stanzas reordered:" in result.output


def test_sort_command_verify(cli_runner, test_conf_file):
    """Test verification functionality."""
    result = cli_runner.invoke(cli, ["sort", "--verify", str(test_conf_file)])
    assert result.exit_code == 0
    assert "Verification passed for" in result.output


def test_sort_command_invalid_file(cli_runner, tmp_path):
    """Test handling of invalid files."""
    # Create a non-conf file
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.touch()

    result = cli_runner.invoke(cli, ["sort", str(invalid_file)])
    assert result.exit_code == 0
    assert "is not a valid configuration file" in result.output


def test_sort_command_multiple_global_stanzas(cli_runner, multiple_global_stanza_file):
    """Test sorting with multiple global stanza types."""
    result = cli_runner.invoke(
        cli, ["sort", "--verbose", str(multiple_global_stanza_file)]
    )
    assert result.exit_code == 0
    # Check for warning about multiple global stanza types
    assert "Multiple global stanza types detected:" in result.output
    # Verify that the file was still sorted successfully
    assert "Sorted:" in result.output

    # Check the content of the sorted file to ensure proper ordering
    with open(multiple_global_stanza_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify global settings are at the top
    assert content.index("global_setting1") < content.index("[]")
    # Verify empty stanza comes before star stanza
    assert content.index("[]") < content.index("[*]")
    # Verify star stanza comes before default stanza
    assert content.index("[*]") < content.index("[default]")
    # Verify default stanza comes before app-specific stanza
    assert content.index("[default]") < content.index("[perfmon]")
    # Verify app-specific stanza comes before source-specific stanza
    assert content.index("[perfmon]") < content.index("[source::example]")
