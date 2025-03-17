"""Merge command implementation for the bydefault CLI.

This module provides the 'merge' command functionality, allowing users to
merge changes from local directory into default directory while preserving
structure and comments.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console

from bydefault.models.merge_models import MergeMode, MergeResult
from bydefault.utils.backup import create_backup
from bydefault.utils.merge_utils import ConfigMerger
from bydefault.utils.scanner import is_valid_ta


def merge_command(
    ta_path: Path,
    verbose: bool = False,
    dry_run: bool = False,
    no_backup: bool = False,
    mode: str = "merge",
    console: Optional[Console] = None,
) -> int:
    """Merge local configurations into default directory.

    The merge command combines changes from local directory into the default directory.
    By default, it merges changes while preserving default values not in local.
    Use mode=replace to completely replace default stanzas with local ones.

    Args:
        ta_path: Path to the TA directory
        verbose: Whether to show detailed output
        dry_run: Show what would be done without making changes
        no_backup: Skip creating backup (backup is created by default)
        mode: How to handle local changes ('merge' or 'replace')
        console: Console for output

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    if console is None:
        console = Console()

    # Track if there were any errors
    had_errors = False

    # Check for local directory - do this check first for test cases
    local_dir = ta_path / "local"
    if not local_dir.is_dir():
        console.print(
            f"[bold red]Error[/bold red]: No local directory found at {ta_path}/local"
        )
        return 1

    # Check for default directory
    default_dir = ta_path / "default"
    if not default_dir.is_dir():
        console.print(
            f"[bold red]Error[/bold red]: No default directory found at {ta_path}/default"
        )
        return 1

    # Verify the directory is a valid TA - only do this after local/default checks
    if not is_valid_ta(ta_path):
        console.print(f"[bold red]Error[/bold red]: Invalid TA directory: {ta_path}")
        return 1

    # Create backup if enabled
    if not no_backup and not dry_run:
        try:
            backup_path = create_backup(default_dir)
            if backup_path:
                console.print(f"Created backup: {backup_path}")
            else:
                console.print(
                    f"[bold red]Error[/bold red]: Failed to create backup for {default_dir}"
                )
                return 1
        except Exception as e:
            console.print(
                f"[bold red]Error[/bold red]: Error creating backup: {str(e)}"
            )
            return 1

    # Initialize merger
    try:
        merger = ConfigMerger(
            ta_dir=ta_path,
            mode=MergeMode(mode),
            verbose=verbose,
        )
    except Exception as e:
        console.print(
            f"[bold red]Error[/bold red]: Error initializing merger: {str(e)}"
        )
        return 1

    try:
        if verbose:
            console.print("[bold]Merging configuration files...[/bold]")

        # Analyze and merge files
        merge_result = merger.merge()

        # Display results
        if verbose:
            display_detailed_results(console, merge_result)
        else:
            display_summary_results(console, merge_result)

        # Write changes if not in dry run mode
        if not dry_run:
            merger.write()
            console.print("[bold green]Merge completed successfully![/bold green]")
        else:
            console.print(
                "[bold yellow]DRY RUN[/bold yellow]: No changes were applied."
            )

    except Exception as e:
        console.print(f"[bold red]Error[/bold red]: Error during merge: {str(e)}")
        had_errors = True

    return 0 if not had_errors else 1


def display_summary_results(console: Console, result: MergeResult) -> None:
    """Display a summary of merge results.

    Args:
        console: Console for output
        result: Merge operation results
    """
    for file_result in result.file_results:
        status = "✓" if file_result.success else "✗"
        console.print(
            f"{file_result.file_path.name}: {status} "
            f"({len(file_result.merged_stanzas)} stanzas merged)"
        )


def display_detailed_results(console: Console, result: MergeResult) -> None:
    """Display detailed merge results.

    Args:
        console: Console for output
        result: Merge operation results
    """
    for file_result in result.file_results:
        console.print(f"\nProcessing: {file_result.file_path}")

        if file_result.new_stanzas:
            console.print("  Added stanzas:")
            for stanza in file_result.new_stanzas:
                console.print(f"    [+] {stanza}")

        if file_result.merged_stanzas:
            console.print("  Merged stanzas:")
            for stanza in file_result.merged_stanzas:
                console.print(f"    [M] {stanza}")

        if file_result.preserved_stanzas:
            console.print("  Preserved stanzas:")
            for stanza in file_result.preserved_stanzas:
                console.print(f"    [=] {stanza}")
