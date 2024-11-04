"""Core functionality for version updates."""

from pathlib import Path
from typing import Optional


def update_version(version: str, ta_path: Optional[Path] = None) -> None:
    """
    Update version in one or all TAs.

    Args:
        version: New version string
        ta_path: Optional path to specific TA. If None, updates all TAs.
    """
    # Basic implementation to make tests pass
    # TODO: Implement actual version update logic
    if not version:
        raise Exception("Version cannot be empty")
