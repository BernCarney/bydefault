"""Command-line interface for byDefault."""

import click
from rich.panel import Panel
from rich.text import Text

from bydefault.utils.output import create_console

console = create_console()


@click.group()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable detailed output",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, verbose: bool, dry_run: bool) -> None:
    """CLI tools for Splunk TA development and maintenance.

    Note: This tool is under active development. The following commands are planned
    but not yet implemented:

    - scan:     Detect and report configuration changes
    - sort:     Sort configuration files maintaining structure
    - merge:    Merge local configurations into default
    - validate: Verify configuration structure and syntax
    - bumpver:  Update version numbers across TAs
    """
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run
    ctx.obj["console"] = console

    if verbose:
        console.print("[bold blue]Verbose output enabled[/]")

    # Show implementation status on root command
    if ctx.invoked_subcommand is None:
        status = Text(
            "\nℹ️  All commands are currently under development.", style="bold yellow"
        )
        console.print(Panel(status, title="Development Status"))
