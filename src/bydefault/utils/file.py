"""File operation utilities."""

from pathlib import Path
from typing import Iterator


def find_conf_files(path: Path, pattern: str = "*.conf") -> Iterator[Path]:
    """
    Find all .conf files in the given path.

    Args:
        path: Directory path to search
        pattern: File pattern to match (default: "*.conf")

    Returns:
        Iterator of Path objects for matching files
    """
    return path.rglob(pattern)
