"""CLI entry point for byDefault."""

import click

from bydefault.cli.merge import merge
from bydefault.cli.version import version
from bydefault.utils.logger import setup_logger

logger = setup_logger()


@click.group()
def main() -> None:
    """byDefault CLI tool for Splunk TA development and maintenance."""
    logger.debug("Starting byDefault CLI")


main.add_command(merge)
main.add_command(version)


if __name__ == "__main__":
    main()
