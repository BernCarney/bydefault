"""CLI entry point for byDefault."""

import click

from bydefault.cli.merge import merge
from bydefault.cli.version import version

__all__ = ["merge", "version"]


@click.group()
def main() -> None:
    """byDefault CLI tool for Splunk TA development and maintenance."""


main.add_command(merge)
main.add_command(version)


if __name__ == "__main__":
    main()
