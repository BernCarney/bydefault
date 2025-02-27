"""Sort command implementation for the bydefault CLI.

This module provides the 'sort' command functionality, allowing users to
sort Splunk configuration files according to Splunk's logical priority
order while preserving structure and comments.
"""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from bydefault.cli import cli
from bydefault.utils.output import format_error, format_success, format_warning
from bydefault.utils.sort_utils import ConfigSorter
from bydefault.utils.validator import validate_file


@cli.command()
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option("--backup", is_flag=True, help="Create backup before sorting")
@click.option("--verify", is_flag=True, help="Verify file structure after sort")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
def sort(
    verbose: bool, dry_run: bool, backup: bool, verify: bool, files: tuple[str, ...]
) -> None:
    """Sort configuration files maintaining structure and comments.

    The sort command organizes stanzas and settings within Splunk configuration files
    while preserving comments and structure.
    """
    console = Console()

    # Process each file
    for file_path in files:
        file_path = Path(file_path)

        # Verify the file is a valid configuration file
        if not file_path.is_file() or not file_path.suffix == ".conf":
            console.print(
                format_error(f"[{file_path}] is not a valid configuration file")
            )
            continue

        # Validate the file before sorting
        if verify:
            console.print(f"Validating: {file_path}")
            validation_result = validate_file(file_path)
            if not validation_result.is_valid:
                console.print(format_error(f"Validation failed for {file_path}:"))
                for error in validation_result.errors:
                    console.print(f"  - {error}")
                continue

        # Create backup if requested
        if backup and not dry_run:
            backup_path = create_backup(file_path)
            if backup_path:
                console.print(f"Created backup: {backup_path}")
            else:
                console.print(format_error(f"Failed to create backup for {file_path}"))
                continue

        # Sort the file
        sorter = ConfigSorter(file_path, verbose=verbose)

        try:
            # Analyze the file
            sorter.parse()

            # Sort the content
            sort_result = sorter.sort()

            # Display results
            if verbose:
                display_detailed_results(console, sort_result)
            else:
                display_summary_results(console, sort_result)

            # Write the sorted file if not in dry run mode
            if not dry_run:
                sorter.write()
                console.print(format_success(f"Sorted: {file_path}"))
            else:
                console.print(
                    format_warning(f"Dry run: No changes made to {file_path}")
                )

            # Verify after sorting if requested
            if verify and not dry_run:
                console.print(f"Verifying after sort: {file_path}")
                validation_result = validate_file(file_path)
                if validation_result.is_valid:
                    console.print(
                        format_success(f"Verification passed for {file_path}")
                    )
                else:
                    console.print(
                        format_error(f"Verification failed after sorting {file_path}:")
                    )
                    for error in validation_result.errors:
                        console.print(f"  - {error}")

        except Exception as e:
            console.print(format_error(f"Error sorting {file_path}: {str(e)}"))


def create_backup(file_path: Path) -> Optional[Path]:
    """Create a backup of the file.

    Args:
        file_path: The path to the file to backup

    Returns:
        Optional[Path]: The backup file path if successful, None otherwise
    """
    try:
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        if backup_path.exists():
            # Find a unique backup name
            i = 1
            while backup_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.bak{i}")
                i += 1

        # Copy the file
        import shutil

        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def display_summary_results(console: Console, sort_result: dict) -> None:
    """Display a summary of the sorting results.

    Args:
        console: The console to print to
        sort_result: The sorting results
    """
    console.print(f"✓ Stanzas reordered: {sort_result.get('stanzas_reordered', 0)}")
    console.print(f"✓ Settings sorted: {sort_result.get('settings_sorted', 0)}")
    console.print(f"✓ Comments preserved: {sort_result.get('comments_preserved', 0)}")


def display_detailed_results(console: Console, sort_result: dict) -> None:
    """Display detailed sorting results.

    Args:
        console: The console to print to
        sort_result: The sorting results
    """
    console.print("Processing global settings...")
    console.print(
        f"  ✓ {sort_result.get('global_settings_count', 0)} settings reordered"
    )

    console.print("Positioning [default] stanza...")
    if sort_result.get("default_stanza_found", False):
        console.print(
            f"  ✓ Stanza moved to position {sort_result.get('default_stanza_position', 0)}"
        )
    else:
        console.print("  ✓ No [default] stanza found")

    console.print("Sorting wildcard stanzas...")
    for stanza in sort_result.get("wildcard_stanzas", []):
        console.print(
            f"  ✓ {stanza} moved to position {sort_result['wildcard_stanzas'][stanza]}"
        )

    console.print("Sorting specific stanzas...")
    for group in sort_result.get("specific_stanzas_groups", []):
        console.print(f"  ✓ {group} group sorted")

    console.print("Preserving comments...")
    console.print(
        f"  ✓ {sort_result.get('comments_preserved', 0)} comment blocks maintained"
    )
