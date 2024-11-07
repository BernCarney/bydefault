"""CLI implementation for version command."""

import click

from bydefault.core.version.update import update_version
from bydefault.utils.logger import setup_logger

logger = setup_logger()


@click.command()
@click.argument("version")
def version(version: str) -> None:
    """Update version number across TAs."""
    try:
        update_version(version)
        logger.info(f"Updated version to {version}")
    except Exception as e:
        logger.error(f"Version update failed: {e}")
        # Exit with error code 1 to indicate failure
        raise click.ClickException(str(e)) from e
