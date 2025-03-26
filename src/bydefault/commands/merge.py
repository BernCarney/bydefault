"""Merge command implementation for the bydefault CLI.

This module provides the 'merge' command functionality, allowing users to
merge changes from local directory into default directory while preserving
structure and comments.
"""

from pathlib import Path
from typing import List, Optional

from rich.console import Console

from bydefault.models.merge_models import MergeMode, MergeResult
from bydefault.utils.backup import create_backup
from bydefault.utils.merge_utils import ConfigMerger
from bydefault.utils.scanner import find_tas, is_valid_ta


def merge_multiple_tas(
    paths: List[Path],
    verbose: bool = False,
    dry_run: bool = False,
    no_backup: bool = False,
    keep_local: bool = False,
    mode: str = "merge",
    recursive: bool = False,
    console: Optional[Console] = None,
) -> int:
    """Merge local configurations into default directory for multiple TAs.

    Handles finding and processing multiple TA directories, including
    recursive discovery.

    Args:
        paths: List of paths to process (TA directories or parent directories)
        verbose: Whether to show detailed output
        dry_run: Show what would be done without making changes
        no_backup: Skip creating backup (backup is created by default)
        keep_local: Keep files in local directory after merging
        (files are removed by default)
        mode: How to handle local changes ('merge' or 'replace')
        recursive: Whether to recursively search for TAs in the directories
        console: Console for output

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    if console is None:
        console = Console()

    # Track if there were any errors
    exit_code = 0

    # Process each TA path
    all_tas = []
    for path in paths:
        if is_valid_ta(path):
            all_tas.append(path)
        elif recursive:
            try:
                found_tas = find_tas(path, recursive=recursive)
                all_tas.extend(found_tas)
            except Exception as e:
                console.print(
                    f"[bold red]Error[/bold red]: Error scanning {path}: {str(e)}"
                )
                exit_code = 1
        else:
            console.print(
                f"[bold yellow]Warning[/bold yellow]: {path} is not a valid Splunk TA. "
                "Use --recursive to search subdirectories."
            )

    if not all_tas:
        console.print(
            "[bold red]Error[/bold red]: No valid Splunk TAs found in the "
            "specified paths"
        )
        return 1

    # Report number of TAs found when processing multiple paths
    if len(all_tas) > 1 or recursive:
        console.print(f"Found {len(all_tas)} Splunk TA directories to process")

    # Process each TA
    for ta_path in all_tas:
        if len(all_tas) > 1:
            console.print(f"\nProcessing: {ta_path}")

        # Run the merge command for this TA
        ta_exit_code = merge_command(
            ta_path=ta_path,
            verbose=verbose,
            dry_run=dry_run,
            no_backup=no_backup,
            keep_local=keep_local,
            mode=mode,
            console=console,
        )

        # Update exit code if there was an error
        if ta_exit_code != 0:
            exit_code = ta_exit_code

    return exit_code


def merge_command(
    ta_path: Path,
    verbose: bool = False,
    dry_run: bool = False,
    no_backup: bool = False,
    keep_local: bool = False,
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
        keep_local: Keep files in local directory after merging
        (files are removed by default)
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
            f"[bold red]Error[/bold red]: No default directory found at "
            f"{ta_path}/default"
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
                    f"[bold red]Error[/bold red]: Failed to create backup for "
                    f"{default_dir}"
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

            # Clean up local files if enabled
            if not keep_local:
                removed_files = merger.cleanup_local_files()
                if removed_files and verbose:
                    console.print("\n[bold]Removed files from local:[/bold]")
                    for file_path in removed_files:
                        console.print(f"  - {file_path.name}")
                elif removed_files:
                    console.print(
                        f"Removed {len(removed_files)} files from local directory"
                    )

            console.print("[bold green]Merge completed successfully![/bold green]")
        else:
            console.print(
                "[bold yellow]DRY RUN[/bold yellow]: No changes were applied."
            )
            if not keep_local:
                console.print(
                    "[bold yellow]Note[/bold yellow]: "
                    "Local files would be removed after merge."
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
