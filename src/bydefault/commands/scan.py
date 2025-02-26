"""
Command implementation for scanning Splunk TA files for changes.

This module implements the scan command functionality, integrating the detection
of TA directories and change detection to provide a comprehensive scan of Splunk
Technology Add-ons.
"""

from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

from bydefault.models.change_detection import ChangeType
from bydefault.utils.change_detection import scan_directory
from bydefault.utils.scanner import find_tas, is_valid_ta


def scan_command(
    paths: List[str],
    baseline: Optional[str] = None,
    recursive: bool = False,
    summary: bool = False,
    details: bool = True,
    console: Optional[Console] = None,
) -> int:
    """
    Scan Splunk TA directories for configuration changes between local and default.

    This command identifies changes made in the local directory compared to the default directory,
    which is essential for understanding what changes need to be merged from local to default.

    Args:
        paths: List of paths to scan
        baseline: Optional baseline path to compare against (advanced use case)
        recursive: Whether to recursively search for TAs in the specified paths
        summary: Whether to show only a summary of changes
        details: Whether to show detailed changes
        console: Optional Rich console instance to use for output (uses custom theme if provided)

    Returns:
        Exit code: 0 for success, non-zero for failure
    """
    # Use provided console or create a new one if not provided
    if console is None:
        console = Console()

    # Validate paths
    valid_paths = []
    for path_str in paths:
        path = Path(path_str).resolve()
        if not path.exists():
            console.print(f"[red]Error: Path {path} does not exist[/red]")
            continue
        valid_paths.append(path)

    if not valid_paths:
        console.print("[red]Error: No valid paths provided[/red]")
        return 1

    # Validate baseline if provided
    baseline_path = None
    if baseline:
        baseline_path = Path(baseline).resolve()
        if not baseline_path.exists():
            console.print(
                f"[red]Error: Baseline path {baseline_path} does not exist[/red]"
            )
            return 1

        if not is_valid_ta(baseline_path):
            console.print(
                f"[red]Error: Baseline path {baseline_path} is not a valid Splunk TA[/red]"
            )
            return 1

    # Find TAs in the specified paths
    all_tas = []
    for path in valid_paths:
        if is_valid_ta(path):
            all_tas.append(path)
        else:
            found_tas = find_tas(path, recursive=recursive)
            all_tas.extend(found_tas)

    if not all_tas:
        console.print("[yellow]No Splunk TAs found in the specified paths[/yellow]")
        return 0

    console.print(f"Found {len(all_tas)} Splunk TA directories to scan")

    # Scan each TA for changes
    scan_results = []
    for ta_path in all_tas:
        try:
            result = scan_directory(ta_path, baseline_path)
            scan_results.append(result)
        except Exception as e:
            console.print(f"[red]Error scanning {ta_path}: {str(e)}[/red]")

    # Display results
    _display_results(console, scan_results, summary, details)

    return 0


def _display_results(console, scan_results, summary=False, details=True):
    """
    Display scan results.

    Args:
        console: Rich console instance
        scan_results: List of ScanResult objects
        summary: Whether to show summary table
        details: Whether to show detailed changes
    """
    # Process each scan result
    for i, result in enumerate(scan_results):
        ta_path = result.ta_path
        ta_name = ta_path.name

        # Add a line break before each TA
        console.print("")

        # Skip invalid TAs
        if not result.is_valid_ta:
            console.print(f"{ta_name}: Not a valid Splunk TA")
            continue

        # Display error message if any
        if result.error_message:
            console.print(f"{ta_name}: {result.error_message}")
            continue

        # Calculate number of changes
        total_changes = len(result.file_changes)

        if total_changes > 0:
            # Display TA header with changes
            console.print(f"Changes detected in: {ta_name}")

            # Group changes by type for more organized display
            added_files = []
            removed_files = []
            modified_files = []

            for file_change in result.file_changes:
                file_path = file_change.file_path

                if file_change.is_new and not file_change.stanza_changes:
                    # New file without stanzas
                    added_files.append(file_change)
                elif not file_change.is_new and not file_change.stanza_changes:
                    # Removed file
                    removed_files.append(file_change)
                else:
                    # Modified file or new file with stanzas
                    modified_files.append(file_change)

            # If detailed view is requested
            if details:
                # Display modified files first
                if modified_files:
                    text = Text("  Modified local files:", style="modification")
                    console.print(text)
                    for file_change in modified_files:
                        file_path = file_change.file_path
                        console.print(f"    {file_path}")

                        # Display stanza changes
                        for stanza_change in file_change.stanza_changes:
                            stanza_name = stanza_change.name

                            # Determine stanza change type and use appropriate colors
                            if stanza_change.change_type == ChangeType.ADDED:
                                # Create a text instance with the stanza name (no markup) and message (with markup)
                                text = Text()
                                text.append(f"      {stanza_name} - ")
                                text.append("New stanza", style="addition")
                                console.print(text)
                            elif stanza_change.change_type == ChangeType.REMOVED:
                                text = Text()
                                text.append(f"      {stanza_name} - ")
                                text.append("Removed stanza", style="deletion")
                                console.print(text)
                            else:
                                text = Text()
                                text.append(f"      {stanza_name} - ")
                                text.append("Modified", style="modification")
                                console.print(text)

                # Display added files
                if added_files:
                    text = Text("  Local files not in default:", style="addition")
                    console.print(text)
                    for file_change in added_files:
                        file_path = file_change.file_path
                        console.print(f"    {file_path}")

                # Display removed files
                if removed_files:
                    text = Text("  Files removed from local:", style="deletion")
                    console.print(text)
                    for file_change in removed_files:
                        file_path = file_change.file_path
                        console.print(f"    {file_path}")

            # If summary view is requested
            elif summary:
                # Create a table for the summary
                table = Table()
                table.add_column("Change Type")
                table.add_column("Count")

                if added_files:
                    table.add_row(
                        Text("Local files not in default", style="addition"),
                        str(len(added_files)),
                    )
                if modified_files:
                    table.add_row(
                        Text("Modified local files", style="modification"),
                        str(len(modified_files)),
                    )
                if removed_files:
                    table.add_row(
                        Text("Files removed from local", style="deletion"),
                        str(len(removed_files)),
                    )

                console.print(table)
        else:
            console.print(f"No changes detected in: {ta_name}")


def add_subparser(subparsers):
    """
    Add the scan command to the CLI subparsers.

    Args:
        subparsers: argparse subparsers object
    """
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan Splunk TA directories for configuration changes",
        description="Scan one or more Splunk TA directories for configuration changes",
    )

    scan_parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to scan (directories or individual TA directories)",
    )

    scan_parser.add_argument(
        "-b",
        "--baseline",
        help="Baseline TA to compare against",
    )

    scan_parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively search for TAs in the specified directories",
    )

    display_group = scan_parser.add_mutually_exclusive_group()
    display_group.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="Show only a summary of changes",
    )
    display_group.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Show detailed changes (default)",
    )

    scan_parser.set_defaults(func=handle_scan_command)


def handle_scan_command(args):
    """
    Handle the scan command from the CLI.

    Args:
        args: Parsed CLI arguments
    """
    return scan_command(
        paths=args.paths,
        baseline=args.baseline,
        recursive=args.recursive,
        summary=args.summary,
        details=args.details
        or not args.summary,  # Default to details if neither flag is set
    )
