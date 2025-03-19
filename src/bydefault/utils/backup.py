"""Utility functions for creating and managing backups."""

import datetime
import shutil
from pathlib import Path
from typing import Optional


def create_backup(path: Path) -> Optional[Path]:
    """Create a backup of a file or directory.

    Args:
        path: Path to the file or directory to back up

    Returns:
        Path to the backup file or directory, or None if backup failed
    """
    if not path.exists():
        return None

    # Generate timestamp for the backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create backup path
    if path.is_file():
        backup_path = path.with_suffix(f"{path.suffix}.{timestamp}.bak")
    else:
        backup_path = path.with_name(f"{path.name}.{timestamp}.bak")

    try:
        # Copy file or directory
        if path.is_file():
            shutil.copy2(path, backup_path)
        else:
            shutil.copytree(path, backup_path)

        return backup_path
    except Exception:
        return None
