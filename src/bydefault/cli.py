"""Command-line interface for byDefault."""

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.theme import Theme

from bydefault import __prog_name__, __version__
from bydefault.commands.scan import scan_command
from bydefault.commands.sort import sort_command
from bydefault.commands.validator import validate_file
from bydefault.utils.output import (
    CHALKY,
    CORAL,
    CYAN,
    IVORY,
    MALIBU,
    SAGE,
    VIOLET,
    WHISKEY,
    print_step_result,
    print_validation_error,
)

# Use existing color scheme from output.py
custom_theme = Theme(
    {
        "success": f"bold {SAGE}",  # Light green from output.py
        "error": f"bold {CORAL}",  # Light red from output.py
        "warning": f"bold {WHISKEY}",  # Light orange from output.py
        "path": MALIBU,  # Light blue from output.py
        "bullet": CHALKY,  # Light yellow from output.py
        "message": IVORY,  # Light gray from output.py
        "line_number": CYAN,  # Cyan from output.py
        "title": VIOLET,  # Purple from output.py
        # Add styles for scan command outputs
        "addition": SAGE,  # Light green for additions
        "modification": CHALKY,  # Light yellow for modifications
        "deletion": CORAL,  # Light red for deletions
    }
)

console = Console(theme=custom_theme)


@click.group()
@click.version_option(
    version=__version__,
    prog_name=__prog_name__,
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """byDefault - CLI tools for Splunk TA development and maintenance.

    A collection of commands designed to assist in Splunk TA development.
    This project is under active development.

    Planned commands:
    - bumpver: Update version numbers across TAs
    """
    # Initialize shared console
    ctx.ensure_object(dict)
    ctx.obj["console"] = console


@cli.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=(
        "Show detailed validation output including file checks, "
        "stanza counts, and specific validation steps."
    ),
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively scan directories for configuration files.",
)
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.pass_context
def validate(
    ctx: click.Context, verbose: bool, recursive: bool, files: tuple[Path, ...]
) -> None:
    """Verify configuration structure and syntax.

    - Non-configuration files will be skipped with a warning.
    - For .conf and .meta files, performs full validation.
    - For other supported files (.conf.spec, .dashboard, .lookup),
      performs basic checks.

    Arguments:
    - FILES: One or more files or directories to validate.
      When directories are specified, only .conf and .meta files will be processed.
      Use --recursive to include subdirectories.

    """
    if not files:
        ctx.obj["console"].print("[error]Error:[/error] No files specified.")
        ctx.obj["console"].print("\nUsage: bydefault validate [OPTIONS] FILES...")
        ctx.obj["console"].print("\nExample usage:")
        ctx.obj["console"].print("  bydefault validate *.conf")
        ctx.obj["console"].print("  bydefault validate default/*.conf default/*.meta")
        ctx.obj["console"].print("  bydefault validate --verbose path/to/props.conf")
        ctx.obj["console"].print(
            "  bydefault validate --recursive path/to/ta_directory"
        )
        ctx.exit(1)

    ctx.obj["verbose"] = verbose

    # Process files and directories
    files_to_validate = []
    for file_path in files:
        if file_path.is_dir():
            if verbose:
                ctx.obj["console"].print(
                    f"[title]Processing directory:[/title] [path]{file_path}[/path]"
                )

            # Find all .conf and .meta files in the directory
            if recursive:
                conf_files = list(file_path.glob("**/*.conf"))
                meta_files = list(file_path.glob("**/*.meta"))
            else:
                conf_files = list(file_path.glob("*.conf"))
                meta_files = list(file_path.glob("*.meta"))

            files_to_validate.extend(conf_files)
            files_to_validate.extend(meta_files)
        else:
            files_to_validate.append(file_path)

    if not files_to_validate:
        ctx.obj["console"].print(
            "[warning]Warning:[/warning] No configuration files found to validate."
        )
        ctx.exit(0)

    previous_had_error = False
    for file_path in files_to_validate:
        # Add newline if previous file had errors
        if previous_had_error:
            ctx.obj["console"].print()

        # Skip directories (already processed)
        if file_path.is_dir():
            continue

        if verbose:
            ctx.obj["console"].print(f"Validating [path]{file_path}[/path]...")

        result = validate_file(
            file_path, verbose=ctx.obj["verbose"], console=ctx.obj["console"]
        )

        # Only show output in non-verbose mode (verbose output handled in validate_file)
        if not verbose:
            ctx.obj["console"].print(f"[path]{file_path}[/path] ", end="")
            # Non-.conf/.meta files get a warning symbol
            if file_path.suffix not in [".conf", ".meta"]:
                print_step_result(ctx.obj["console"], "warning")
            else:
                print_step_result(ctx.obj["console"], result.is_valid)
                if not result.is_valid:
                    for issue in result.issues:
                        print_validation_error(
                            ctx.obj["console"], issue.line_number, issue.message
                        )

        # Update error state for next iteration
        previous_had_error = not result.is_valid and file_path.suffix in [
            ".conf",
            ".meta",
        ]

    # Add final newline
    if not verbose:
        ctx.obj["console"].print()


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "-b",
    "--baseline",
    help="Baseline TA to compare against",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    help="Recursively search for TAs in the specified directories",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show more detailed output",
)
@click.option(
    "-s",
    "--summary",
    is_flag=True,
    help="Show only a summary of changes",
)
@click.option(
    "-d",
    "--details",
    is_flag=True,
    help="Show detailed changes (default)",
)
@click.option(
    "--include-removed",
    is_flag=True,
    help="Include files and stanzas that exist in default but not in local",
)
@click.pass_context
def scan(
    ctx: click.Context,
    paths: tuple[Path, ...],
    baseline: Path,
    recursive: bool,
    verbose: bool,
    summary: bool,
    details: bool,
    include_removed: bool,
) -> None:
    """Scan Splunk TA directories for configuration changes.

    Detects and reports changes in Splunk TA configuration files,
    comparing against a baseline or reporting all configurations.

    Arguments:
    - PATHS: One or more paths to scan (directories or individual TA directories)

    """
    if not paths:
        ctx.obj["console"].print("[error]Error:[/error] No paths specified.")
        ctx.obj["console"].print("\nUsage: bydefault scan [OPTIONS] PATHS...")
        ctx.obj["console"].print("\nExample usage:")
        ctx.obj["console"].print("  bydefault scan path/to/ta")
        ctx.obj["console"].print(
            "  bydefault scan -b baseline_ta path/to/ta1 path/to/ta2"
        )
        ctx.obj["console"].print("  bydefault scan -r -s path/containing/tas")
        ctx.exit(1)

    # Convert to strings for the scan_command function
    path_strings = [str(path) for path in paths]
    baseline_string = str(baseline) if baseline else None

    exit_code = scan_command(
        paths=path_strings,
        baseline=baseline_string,
        recursive=recursive,
        verbose=verbose,
        summary=summary,
        details=details or not summary,  # Default to details if neither flag is set
        include_removed=include_removed,
        console=ctx.obj["console"],
    )

    ctx.exit(exit_code)


@cli.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--backup",
    "-b",
    is_flag=True,
    help="Create backup before sorting",
)
@click.option(
    "--verify",
    "-c",
    is_flag=True,
    help="Verify file structure after sort",
)
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.pass_context
def sort(
    ctx: click.Context,
    verbose: bool,
    dry_run: bool,
    backup: bool,
    verify: bool,
    files: tuple[Path, ...],
) -> None:
    """Sort configuration files maintaining structure and comments.

    The sort command organizes stanzas and settings within Splunk configuration files
    while preserving comments and structure.

    Arguments:
    - FILES: One or more configuration files to sort
    """
    if not files:
        ctx.obj["console"].print("[error]Error:[/error] No files specified.")
        ctx.obj["console"].print("\nUsage: bydefault sort [OPTIONS] FILES...")
        ctx.obj["console"].print("\nExample usage:")
        ctx.obj["console"].print("  bydefault sort path/to/props.conf")
        ctx.obj["console"].print("  bydefault sort --dry-run path/to/*.conf")
        ctx.obj["console"].print(
            "  bydefault sort --backup --verify path/to/props.conf"
        )
        ctx.exit(1)

    # Convert Paths to strings for the sort_command function
    files_str = [str(f) for f in files]

    exit_code = sort_command(
        files=files_str,
        verbose=verbose,
        dry_run=dry_run,
        backup=backup,
        verify=verify,
        console=ctx.obj["console"],
    )

    ctx.exit(exit_code)


@cli.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Skip creating backup before merging (backup is created by default)",
)
@click.option(
    "--keep-local",
    is_flag=True,
    help="Keep files in local directory after merging (files are removed by default)",
)
@click.option(
    "--mode",
    type=click.Choice(["merge", "replace"], case_sensitive=False),
    default="merge",
    help=(
        "Merge mode: 'merge' combines settings, 'replace' completely "
        "replaces default stanzas with local ones"
    ),
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively search for TAs in the specified directories",
)
@click.argument(
    "paths", nargs=-1, type=click.Path(exists=True, path_type=Path), required=True
)
@click.pass_context
def merge(
    ctx: click.Context,
    verbose: bool,
    dry_run: bool,
    no_backup: bool,
    keep_local: bool,
    mode: str,
    recursive: bool,
    paths: tuple[Path, ...],
) -> None:
    """Merge changes from local directory into default directory.

    Takes changes from the 'local' directory in a TA and merges them into
    the 'default' directory, preserving structure and comments.

    By default, a backup is created unless --no-backup is specified.
    After a successful merge, files in local are removed unless --keep-local
    is specified.

    Arguments:
    - PATHS: One or more paths to Splunk TA directories
      (or parent directories with --recursive)

    """
    if not paths:
        ctx.obj["console"].print("[error]Error:[/error] No paths specified.")
        ctx.obj["console"].print("\nUsage: bydefault merge [OPTIONS] PATHS...")
        ctx.obj["console"].print("\nExample usage:")
        ctx.obj["console"].print("  bydefault merge path/to/ta")
        ctx.obj["console"].print("  bydefault merge --verbose path/to/ta")
        ctx.obj["console"].print("  bydefault merge --dry-run path/to/ta")
        ctx.obj["console"].print("  bydefault merge --mode replace path/to/ta")
        ctx.obj["console"].print("  bydefault merge --keep-local path/to/ta")
        ctx.obj["console"].print("  bydefault merge -r parent/directory/with/tas")
        ctx.exit(1)

    # Import here to avoid circular import issues
    from bydefault.commands.merge import merge_multiple_tas

    # Use the new function to handle multiple TAs
    exit_code = merge_multiple_tas(
        paths=list(paths),
        verbose=verbose,
        dry_run=dry_run,
        no_backup=no_backup,
        keep_local=keep_local,
        mode=mode,
        recursive=recursive,
        console=ctx.obj["console"],
    )

    ctx.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    cli()
