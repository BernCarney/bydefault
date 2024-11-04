"""CLI implementation for merge command."""

from pathlib import Path
from typing import Optional, TypeAlias

import click

from bydefault.utils import (
    InvalidWorkingDirectoryError,
    setup_logger,
    validate_working_context,
)

logger = setup_logger()

TAPath: TypeAlias = Optional[Path]


@click.command()
@click.argument("ta_name", required=False)
def merge(ta_name: Optional[str] = None) -> None:
    """
    Merge local configurations into default.

    Validates the working context and processes configuration merges for one or all TAs.
    The command can be run from:
    1. Inside a TA directory (merges that TA)
    2. Inside a directory containing TAs (merges all TAs)
    3. Inside a git repository with TAs (merges all TAs)

    Args:
        ta_name: Optional name of specific TA to merge. If not provided,
                processes all TAs in the current context.

    Raises:
        click.ClickException: If working directory is invalid or merge fails
    """
    try:
        working_dir = validate_working_context(Path.cwd())
        ta_path: TAPath = Path(working_dir / ta_name) if ta_name else None

        # TODO: Implement merge functionality
        logger.info("Merge functionality not yet implemented")
        logger.debug(f"Would merge: {'all TAs' if ta_name is None else ta_name}")

    except InvalidWorkingDirectoryError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise click.ClickException(str(e)) from e
