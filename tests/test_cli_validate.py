"""Tests for the validate command CLI interface."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from bydefault.cli import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_validate_file():
    """Mock the validate_file function."""
    with patch("bydefault.cli.validate_file") as mock:
        yield mock


@pytest.fixture
def test_files(tmp_path):
    """Create test files for validation."""
    file1 = tmp_path / "test1.conf"
    file2 = tmp_path / "test2.conf"
    file1.touch()
    file2.touch()
    return [file1, file2]


def test_validate_basic(runner, mock_validate_file, test_files):
    """Test basic validate command."""
    mock_validate_file.return_value.is_valid = True

    result = runner.invoke(cli, ["validate", str(test_files[0])])
    assert result.exit_code == 0
    mock_validate_file.assert_called_once()


def test_validate_verbose(runner, mock_validate_file, test_files):
    """Test validate command with verbose flag."""
    result = runner.invoke(cli, ["validate", "--verbose", str(test_files[0])])
    assert result.exit_code == 0
    assert mock_validate_file.call_args[1]["verbose"] is True


def test_validate_multiple_files(runner, mock_validate_file, test_files):
    """Test validating multiple files."""
    mock_validate_file.return_value.is_valid = True

    result = runner.invoke(cli, ["validate", str(test_files[0]), str(test_files[1])])
    assert result.exit_code == 0
    assert mock_validate_file.call_count == len(test_files)


def test_validate_error_handling(runner, mock_validate_file, test_files):
    """Test handling validation errors."""
    mock_validate_file.return_value.is_valid = False
    mock_validate_file.return_value.issues = [Mock(line_number=1, message="Test error")]

    result = runner.invoke(cli, ["validate", str(test_files[0])])
    assert result.exit_code == 0  # CLI should complete even with validation errors


def test_validate_no_files(runner):
    """Test validate command with no files."""
    result = runner.invoke(cli, ["validate"])
    assert result.exit_code == 1  # Should fail with no files
    assert "Error: No files specified" in result.output
    assert "Example usage:" in result.output
    assert "bydefault validate *.conf" in result.output


def test_validate_help(runner):
    """Test validate command help text."""
    result = runner.invoke(cli, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Verify configuration structure and syntax" in result.output
    assert "Validates Splunk configuration files" in result.output
    assert "Non-configuration files will be skipped" in result.output
    assert "--verbose" in result.output


def test_validate_nonexistent_file(runner):
    """Test validate command with nonexistent file."""
    result = runner.invoke(cli, ["validate", "nonexistent.conf"])
    assert result.exit_code != 0  # Should fail for nonexistent files


def test_validate_console_output(runner, mock_validate_file, test_files):
    """Test validate command console output formatting."""
    mock_validate_file.return_value.is_valid = True
    mock_validate_file.return_value.file_path = test_files[0]
    mock_validate_file.return_value.stats = {"lines": 10, "stanzas": 2}

    result = runner.invoke(cli, ["validate", "--verbose", str(test_files[0])])
    assert result.exit_code == 0
    # Verify we get some output
    assert result.output
    # Verify newlines at start and end
    assert result.output.startswith("\n") or result.output.endswith("\n")
