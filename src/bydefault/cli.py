"""Command-line interface for byDefault."""

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.theme import Theme

from bydefault import __prog_name__, __version__
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
@click.version_option(version=__version__, prog_name=__prog_name__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CLI tools for Splunk TA development and maintenance.

    A collection of tools for developing and maintaining Splunk Technology
    Add-ons (TAs). Implemented commands can be found in the help text below.

    Currently under active development with the following planned commands:
    - scan:     Detect and report configuration changes
    - sort:     Sort configuration files maintaining structure
    - merge:    Merge local configurations into default
    - bumpver:  Update version numbers across TAs
    """
    # Initialize context object with default values
    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "verbose": False,
            "console": console,
        }
    )


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


if __name__ == "__main__":  # pragma: no cover
    cli()
