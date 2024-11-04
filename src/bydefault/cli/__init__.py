"""CLI entry point for byDefault."""

import click

from bydefault.cli.merge import merge
from bydefault.cli.version import version


@click.group()
def main() -> None:
    """byDefault CLI tool for Splunk TA development."""
    pass


main.add_command(merge)
main.add_command(version)


if __name__ == "__main__":
    main()
