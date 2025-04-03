"""Tests for the merge command functionality."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from bydefault.commands.merge import merge_command


@pytest.fixture
def mock_console():
    """Fixture providing a mock console."""
    return MagicMock(spec=Console)


@pytest.fixture
def ta_dir(tmp_path):
    """Create a temporary TA directory structure for testing."""
    ta = tmp_path / "test_ta"
    ta.mkdir()

    local = ta / "local"
    default = ta / "default"
    metadata = ta / "metadata"
    local.mkdir()
    default.mkdir()
    metadata.mkdir()

    # Create a sample conf file in local
    local_file = local / "inputs.conf"
    local_file.write_text(
        """
[monitor://test]
index = main
sourcetype = test
disabled = false

[monitor://another]
index = security
sourcetype = security_logs
disabled = false
"""
    )

    # Create a sample conf file in default
    default_file = default / "inputs.conf"
    default_file.write_text(
        """
[monitor://test]
index = main
sourcetype = test
disabled = true

[monitor://existing]
index = internal
sourcetype = internal_logs
disabled = true
"""
    )

    # Create metadata files
    local_meta = metadata / "local.meta"
    local_meta.write_text(
        """
[monitor://test]
access = read : [ * ], write : [ admin ]
export = system
owner = admin
version = 8.2.3

[monitor://another]
access = read : [ * ], write : [ admin ]
owner = admin
"""
    )

    default_meta = metadata / "default.meta"
    default_meta.write_text(
        """
[monitor://test]
access = read : [ * ], write : [ admin ]
owner = nobody
version = 8.2.0

[monitor://existing]
access = read : [ * ], write : [ admin ]
owner = nobody
"""
    )

    return ta


def test_merge_invalid_ta_path(mock_console):
    """Test merge command with invalid TA path."""
    result = merge_command(
        Path("/nonexistent"),
        verbose=False,
        dry_run=False,
        no_backup=False,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 1
    mock_console.print.assert_called_with(
        "[bold red]Error[/bold red]: No local directory found at /nonexistent/local"
    )


def test_merge_missing_local_dir(tmp_path, mock_console):
    """Test merge command with missing local directory."""
    ta = tmp_path / "test_ta"
    ta.mkdir()
    (ta / "default").mkdir()

    result = merge_command(
        ta,
        verbose=False,
        dry_run=False,
        no_backup=False,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 1
    mock_console.print.assert_called_with(
        f"[bold red]Error[/bold red]: No local directory found at {ta}/local"
    )


def test_merge_missing_default_dir(tmp_path, mock_console):
    """Test merge command with missing default directory."""
    ta = tmp_path / "test_ta"
    ta.mkdir()
    (ta / "local").mkdir()

    result = merge_command(
        ta,
        verbose=False,
        dry_run=False,
        no_backup=False,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 1
    mock_console.print.assert_called_with(
        f"[bold red]Error[/bold red]: No default directory found at {ta}/default"
    )


def test_merge_successful(ta_dir, mock_console):
    """Test successful merge command execution."""
    # Print initial content for debugging
    local_file = ta_dir / "local" / "inputs.conf"
    default_file = ta_dir / "default" / "inputs.conf"
    print(f"\nBEFORE MERGE - Local content:\n{local_file.read_text()}")
    print(f"\nBEFORE MERGE - Default content:\n{default_file.read_text()}")

    # Call the merge command
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=True,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify merged file content
    content = default_file.read_text()
    print(f"\nAFTER MERGE - Default content:\n{content}")

    # Check for merged entries
    assert "monitor://test" in content
    assert "monitor://another" in content  # New stanza from local
    assert "monitor://existing" in content  # Preserved from default
    assert "disabled = false" in content  # Updated value from local

    # Success message
    mock_console.print.assert_any_call(
        "[bold green]Merge completed successfully![/bold green]"
    )


def test_merge_dry_run(ta_dir, mock_console):
    """Test merge command in dry run mode."""
    # Print initial content for debugging
    local_file = ta_dir / "local" / "inputs.conf"
    default_file = ta_dir / "default" / "inputs.conf"
    print(f"\nBEFORE DRY RUN - Local content:\n{local_file.read_text()}")
    print(f"\nBEFORE DRY RUN - Default content:\n{default_file.read_text()}")

    orig_content = default_file.read_text()

    # Call the merge command in dry run mode
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=True,
        no_backup=True,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify file was not changed
    content = default_file.read_text()
    print(f"\nAFTER DRY RUN - Default content:\n{content}")
    assert content == orig_content

    # Dry run message
    mock_console.print.assert_any_call(
        "[bold yellow]DRY RUN[/bold yellow]: No changes were applied."
    )


def test_merge_with_backup(ta_dir, mock_console):
    """Test merge command with backup creation."""
    with patch("bydefault.commands.merge.create_backup") as mock_backup:
        result = merge_command(
            ta_dir,
            verbose=False,
            dry_run=False,
            no_backup=False,
            keep_local=True,
            mode="merge",
            console=mock_console,
        )

        assert result == 0
        mock_backup.assert_called_once()


def test_merge_without_backup(ta_dir, mock_console):
    """Test merge command without backup creation."""
    with patch("bydefault.commands.merge.create_backup") as mock_backup:
        result = merge_command(
            ta_dir,
            verbose=False,
            dry_run=False,
            no_backup=True,
            keep_local=True,
            mode="merge",
            console=mock_console,
        )

        assert result == 0
        mock_backup.assert_not_called()


def test_merge_replace_mode(ta_dir, mock_console):
    """Test merge command in replace mode."""
    # Print initial content for debugging
    local_file = ta_dir / "local" / "inputs.conf"
    default_file = ta_dir / "default" / "inputs.conf"
    print(f"\nBEFORE MERGE - Local content:\n{local_file.read_text()}")
    print(f"\nBEFORE MERGE - Default content:\n{default_file.read_text()}")

    # Call the merge command in replace mode
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=True,
        keep_local=True,
        mode="replace",
        console=mock_console,
    )

    assert result == 0

    # Verify merged file content
    content = default_file.read_text()
    print(f"\nAFTER MERGE - Default content:\n{content}")

    # Check for complete replacement of stanzas
    assert "monitor://test" in content
    assert "monitor://another" in content  # New stanza from local
    assert "monitor://existing" in content  # Should still be preserved

    # In the test stanza, check that values were completely replaced
    assert "disabled = false" in content  # From local

    # Success message
    mock_console.print.assert_any_call(
        "[bold green]Merge completed successfully![/bold green]"
    )


def test_merge_verbose_output(ta_dir, mock_console):
    """Test merge command with verbose output."""
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=False,
        keep_local=True,
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Check for verbose output
    mock_console.print.assert_any_call("[bold]Merging configuration files...[/bold]")
    # More verbose messages should be checked depending on implementation details


def test_merge_cleanup_local(ta_dir, mock_console):
    """Test merge command removes local files after successful merge."""
    # Print initial content for debugging
    local_file = ta_dir / "local" / "inputs.conf"
    default_file = ta_dir / "default" / "inputs.conf"
    print(f"\nBEFORE MERGE - Local content:\n{local_file.read_text()}")
    print(f"\nBEFORE MERGE - Default content:\n{default_file.read_text()}")

    # Call the merge command with cleanup enabled (default behavior)
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=True,
        keep_local=False,  # Default behavior is to remove local files
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify local file was removed
    assert not os.path.exists(local_file)

    # Verify merged file content in default
    content = default_file.read_text()
    print(f"\nAFTER MERGE - Default content:\n{content}")

    # Success messages
    mock_console.print.assert_any_call(
        "[bold green]Merge completed successfully![/bold green]"
    )


def test_merge_keep_local(ta_dir, mock_console):
    """Test merge command keeps local files when keep_local is True."""
    # Print initial content for debugging
    local_file = ta_dir / "local" / "inputs.conf"
    default_file = ta_dir / "default" / "inputs.conf"
    print(f"\nBEFORE MERGE - Local content:\n{local_file.read_text()}")
    print(f"\nBEFORE MERGE - Default content:\n{default_file.read_text()}")

    # Call the merge command with keep_local=True
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=True,
        keep_local=True,  # Keep local files
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify local file was not removed
    assert os.path.exists(local_file)

    # Success message
    mock_console.print.assert_any_call(
        "[bold green]Merge completed successfully![/bold green]"
    )


def test_merge_dry_run_no_cleanup(ta_dir, mock_console):
    """Test merge command doesn't remove local files in dry run mode."""
    local_file = ta_dir / "local" / "inputs.conf"

    # Call the merge command in dry run mode with cleanup enabled
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=True,
        no_backup=True,
        keep_local=False,  # Would remove local files if not in dry run
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify local file was not removed
    assert os.path.exists(local_file)

    # Check for dry run message about cleanup
    mock_console.print.assert_any_call(
        "[bold yellow]Note[/bold yellow]: Local files would be removed after merge."
    )


def test_merge_metadata_files(ta_dir, mock_console):
    """Test that metadata files are correctly processed during merge."""
    # Print initial content for debugging
    local_meta = ta_dir / "metadata" / "local.meta"
    default_meta = ta_dir / "metadata" / "default.meta"

    print(f"\nBEFORE MERGE - Local.meta content:\n{local_meta.read_text()}")
    print(f"\nBEFORE MERGE - Default.meta content:\n{default_meta.read_text()}")

    # Call the merge command
    result = merge_command(
        ta_dir,
        verbose=True,
        dry_run=False,
        no_backup=True,
        keep_local=False,  # Don't keep local meta file
        mode="merge",
        console=mock_console,
    )

    assert result == 0

    # Verify merged metadata content
    merged_content = default_meta.read_text()
    print(f"\nAFTER MERGE - Default.meta content:\n{merged_content}")

    # Check for merged metadata entries
    assert "[monitor://test]" in merged_content
    assert "[monitor://another]" in merged_content
    assert "[monitor://existing]" in merged_content
    assert "owner = admin" in merged_content  # From local.meta
    assert "export = system" in merged_content  # From local.meta

    # Verify local.meta was removed
    assert not local_meta.exists()

    # Success message
    mock_console.print.assert_any_call(
        "[bold green]Merge completed successfully![/bold green]"
    )
