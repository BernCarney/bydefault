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
