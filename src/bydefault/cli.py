"""Command-line interface for byDefault."""

import rich_click as click

from bydefault import __prog_name__, __version__


@click.group()
@click.version_option(version=__version__, prog_name=__prog_name__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """CLI tools for Splunk TA development and maintenance.

    \b
    A collection of tools for developing and maintaining Splunk Technology Add-ons (TAs).
    Currently under active development with the following planned commands:

    \b
    - scan:     Detect and report configuration changes
    - sort:     Sort configuration files maintaining structure
    - merge:    Merge local configurations into default
    - validate: Verify configuration structure and syntax
    - bumpver:  Update version numbers across TAs
    """
    if ctx.obj is None:
        ctx.obj = {}


if __name__ == "__main__":
    cli()
