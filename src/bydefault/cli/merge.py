"""CLI implementation for merge command."""

from pathlib import Path
from typing import Optional, TypeAlias

import click

from bydefault.core.merge.conf import process_merge
from bydefault.utils.file import InvalidWorkingDirectoryError, validate_working_context
from bydefault.utils.logger import setup_logger

logger = setup_logger()

TAPath: TypeAlias = Optional[Path]  # New in Python 3.10+


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
        process_merge(ta_path)
        logger.info(f"Merged {'all TAs' if ta_name is None else ta_name}")

    except InvalidWorkingDirectoryError as e:
        logger.error(str(e))
        raise click.ClickException(str(e)) from e
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise click.ClickException(str(e)) from e
