"""Command-line interface for byDefault."""

from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.theme import Theme

from bydefault import __prog_name__, __version__
from bydefault.commands.validator import validate_file
from bydefault.utils.output import CHALKY, CORAL, CYAN, IVORY, MALIBU, SAGE

# Use existing color scheme from output.py
custom_theme = Theme(
    {
        "success": f"bold {SAGE}",  # Light green from output.py
        "error": f"bold {CORAL}",  # Light red from output.py
        "path": MALIBU,  # Light blue from output.py
        "bullet": CHALKY,  # Light yellow from output.py
        "message": IVORY,  # Light gray from output.py
        "line_number": CYAN,  # Cyan from output.py
    }
)

console = Console(theme=custom_theme)


@click.group()
@click.version_option(version=__version__, prog_name=__prog_name__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CLI tools for Splunk TA development and maintenance.

    \b
    A collection of tools for developing and maintaining Splunk Technology
    Add-ons (TAs).

    \b
    Currently under active development with the following planned commands:

    \b
    - scan:     Detect and report configuration changes
    - sort:     Sort configuration files maintaining structure
    - merge:    Merge local configurations into default
    - bumpver:  Update version numbers across TAs
    """
    if ctx.obj is None:
        ctx.obj = {}


@cli.command()
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option("--report", is_flag=True, help="Generate validation report")
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
def validate(
    verbose: bool, dry_run: bool, report: bool, files: tuple[Path, ...]
) -> None:
    """Verify configuration structure and syntax."""
    for i, file_path in enumerate(files):
        # Add newline before file if not first file and previous had errors
        if i > 0 and not validate_file(files[i - 1]).is_valid:
            console.print()

        result = validate_file(file_path)
        if result.is_valid:
            console.print(f"[path]{file_path}[/path] [success]✓[/success]")
        else:
            console.print(f"[path]{file_path}[/path] [error]✗[/error]")
            for issue in result.issues:
                console.print(
                    f"  [bullet]•[/bullet] Line [line_number]{issue.line_number}[/line_number]: "
                    f"[message]{issue.message}[/message]"
                )

    # Add final newline
    console.print()


if __name__ == "__main__":  # pragma: no cover
    cli()
