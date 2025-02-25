"""Command-line interface for byDefault."""

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.theme import Theme

from bydefault import __prog_name__, __version__
from bydefault.commands.scan import scan_command
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
    - scan: Detect and report configuration changes
    - sort: Sort configuration files while maintaining structure
    - merge: Merge local configurations into default
    - bumpver: Update version numbers across TAs
    """
    # Initialize shared console
    ctx.ensure_object(dict)
    ctx.obj["console"] = console


@cli.command()
@click.option(
    "--verbose",
    is_flag=True,
    help=(
        "Show detailed validation output including file checks, "
        "stanza counts, and specific validation steps."
    ),
)
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.pass_context
def validate(ctx: click.Context, verbose: bool, files: tuple[Path, ...]) -> None:
    """Verify configuration structure and syntax.

    - Non-configuration files will be skipped with a warning.
    - For .conf and .meta files, performs full validation.
    - For other supported files (.conf.spec, .dashboard, .lookup),
      performs basic checks.

    Arguments:
    - FILES: One or more files or glob patterns to validate.

    """
    if not files:
        ctx.obj["console"].print("[error]Error:[/error] No files specified.")
        ctx.obj["console"].print("\nUsage: bydefault validate [OPTIONS] FILES...")
        ctx.obj["console"].print("\nExample usage:")
        ctx.obj["console"].print("  bydefault validate *.conf")
        ctx.obj["console"].print("  bydefault validate default/*.conf default/*.meta")
        ctx.obj["console"].print("  bydefault validate --verbose path/to/props.conf")
        ctx.obj["console"].print("  bydefault validate --verbose path/to/props.conf")
        ctx.exit(1)

    ctx.obj["verbose"] = verbose

    previous_had_error = False
    for file_path in files:
        # Skip directories in output but still process files within them
        if file_path.is_dir():
            if verbose:
                ctx.obj["console"].print(
                    f"[title]Processing directory:[/title] [path]{file_path}[/path]"
                )
            continue

        # Add newline if previous file had errors
        if previous_had_error:
            ctx.obj["console"].print()

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
@click.pass_context
def scan(
    ctx: click.Context,
    paths: tuple[Path, ...],
    baseline: Path,
    recursive: bool,
    summary: bool,
    details: bool,
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

    # Default to details if neither flag is set
    if not summary and not details:
        details = True

    exit_code = scan_command(
        paths=path_strings,
        baseline=baseline_string,
        recursive=recursive,
        summary=summary,
        details=details,
    )

    ctx.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    cli()
