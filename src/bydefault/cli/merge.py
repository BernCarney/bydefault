"""CLI implementation for merge command."""

from pathlib import Path
from typing import Optional

import click

from bydefault.core.merge.conf import process_merge
from bydefault.utils.logger import setup_logger

logger = setup_logger()


@click.command()
@click.argument("ta_name", required=False)
def merge(ta_name: Optional[str] = None) -> None:
    """Merge local configurations into default."""
    try:
        ta_path = Path(ta_name) if ta_name else None
        process_merge(ta_path)
        logger.info(f"Merged {'all TAs' if ta_name is None else ta_name}")
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise click.ClickException(str(e))
