"""CLI implementation for merge command."""

from pathlib import Path
from typing import Optional

import click

from bydefault.core.merge.conf import process_merge
from bydefault.utils.file import InvalidWorkingDirectoryError, validate_working_context
from bydefault.utils.logger import setup_logger

logger = setup_logger()


@click.command()
@click.argument("ta_name", required=False)
def merge(ta_name: Optional[str] = None) -> None:
    """
    Merge local configurations into default.

    Args:
        ta_name: Optional name of specific TA to merge
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate working context
        working_dir = validate_working_context(cwd)

        # If ta_name is provided, construct full path
        ta_path = Path(working_dir / ta_name) if ta_name else None

        # Process merge with validated path
        process_merge(ta_path)

        logger.info(f"Merged {'all TAs' if ta_name is None else ta_name}")

    except InvalidWorkingDirectoryError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise click.ClickException(str(e)) from e
