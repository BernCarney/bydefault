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

from bydefault.models.change_detection import ChangeType
from bydefault.utils.change_detection import scan_directory
from bydefault.utils.scanner import find_tas, is_valid_ta


def scan_command(
    paths: List[str],
    baseline: Optional[str] = None,
    recursive: bool = False,
    summary: bool = False,
    details: bool = True,
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

    Returns:
        Exit code: 0 for success, non-zero for failure
    """
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


def _display_results(console, scan_results, summary, details):
    """
    Display scan results to the user, showing changes between local and default.

    Args:
        console: Rich console instance
        scan_results: List of ScanResult objects
        summary: Whether to show only a summary
        details: Whether to show detailed changes
    """
    console.print("\n[bold]Scan Results:[/bold]")

    for result in scan_results:
        ta_name = result.ta_path.name

        if not result.is_valid_ta:
            console.print(f"[yellow]{ta_name}:[/yellow] Not a valid Splunk TA")
            continue

        if result.error_message:
            console.print(f"[red]{ta_name}:[/red] {result.error_message}")
            continue

        # Count changes by type
        added_files = 0
        removed_files = 0
        modified_files = 0

        for file_change in result.file_changes:
            if file_change.is_new:
                added_files += 1
            elif not file_change.stanza_changes:  # Removed files have no stanza changes
                removed_files += 1
            else:
                modified_files += 1

        total_changes = added_files + removed_files + modified_files

        # Display header for this TA
        if total_changes > 0:
            header = f"{ta_name}: {total_changes} changes detected in local"
            console.print(f"\n[bold green]{header}[/bold green]")

            if summary:
                # Display summary table
                summary_table = Table(show_header=True, header_style="bold")
                summary_table.add_column("Change Type")
                summary_table.add_column("Count", justify="right")

                if added_files > 0:
                    summary_table.add_row(
                        "Files in local not in default", str(added_files)
                    )
                if removed_files > 0:
                    summary_table.add_row(
                        "Files in default not in local", str(removed_files)
                    )
                if modified_files > 0:
                    summary_table.add_row(
                        "Files modified in local", str(modified_files)
                    )

                console.print(summary_table)

            if details:
                # Display detailed changes
                for file_change in result.file_changes:
                    file_path = file_change.file_path

                    if file_change.is_new:
                        change_type = "[green]ADDED IN LOCAL[/green]"
                    elif not file_change.stanza_changes:
                        change_type = "[red]NOT IN LOCAL[/red]"
                    else:
                        change_type = "[yellow]MODIFIED IN LOCAL[/yellow]"

                    console.print(f"\n  {change_type} {file_path}")

                    if file_change.stanza_changes:
                        for stanza_change in file_change.stanza_changes:
                            stanza_name = stanza_change.name

                            if stanza_change.change_type == ChangeType.ADDED:
                                stanza_type = "[green]ADDED IN LOCAL[/green]"
                            elif stanza_change.change_type == ChangeType.REMOVED:
                                stanza_type = "[red]NOT IN LOCAL[/red]"
                            else:
                                stanza_type = "[yellow]MODIFIED IN LOCAL[/yellow]"

                            console.print(f"    {stanza_type} [{stanza_name}]")

                            # Show setting changes
                            for setting_change in stanza_change.setting_changes:
                                setting_name = setting_change.name

                                if setting_change.change_type == ChangeType.ADDED:
                                    setting_str = f"[green]+{setting_name} = {setting_change.local_value} (in local)[/green]"
                                elif setting_change.change_type == ChangeType.REMOVED:
                                    setting_str = f"[red]-{setting_name} = {setting_change.default_value} (in default)[/red]"
                                else:
                                    setting_str = (
                                        f"[yellow]{setting_name} = "
                                        f"{setting_change.default_value} (default) → {setting_change.local_value} (local)[/yellow]"
                                    )

                                console.print(f"      {setting_str}")
        else:
            console.print(
                f"\n[blue]{ta_name}:[/blue] No changes detected between local and default"
            )


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
