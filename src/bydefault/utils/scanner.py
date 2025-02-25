"""Implementation for scanning Splunk TAs for configuration changes.

This module provides functions for detecting valid TA structures and scanning
for configuration changes between local and default directories.
"""

from pathlib import Path
from typing import List, Set


def is_valid_ta(path: Path) -> bool:
    """Check if a directory has valid TA structure.

    A valid TA must have:
    - A 'default' directory
    - An 'app.conf' file in default directory OR at least one .conf file

    Args:
        path: Directory to check

    Returns:
        bool: True if directory appears to be a valid TA
    """
    # Must be a directory
    if not path.is_dir():
        return False

    # Check for default directory
    default_dir = path / "default"
    if not default_dir.is_dir():
        return False

    # Check for app.conf
    app_conf = default_dir / "app.conf"
    if app_conf.is_file():
        return True

    # If no app.conf, check for at least one .conf file
    conf_files = list(default_dir.glob("*.conf"))
    if conf_files:
        return True

    return False


def find_tas(base_path: Path, recursive: bool = False) -> List[Path]:
    """Find Splunk TAs in a directory.

    Scans a directory for valid Splunk TA structures. If the directory itself
    is a TA, it's returned directly. Otherwise, searches for TAs in direct
    children or recursively if specified.

    Args:
        base_path: Starting directory
        recursive: Whether to search subdirectories

    Returns:
        List[Path]: Paths to valid TAs

    Raises:
        FileNotFoundError: If base_path doesn't exist
        NotADirectoryError: If base_path is not a directory
    """
    # Validate base path
    if not base_path.exists():
        raise FileNotFoundError(f"Path does not exist: {base_path}")
    if not base_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {base_path}")

    # If base_path is a TA, return it directly
    if is_valid_ta(base_path):
        return [base_path]

    # Search for TAs in direct children
    tas: List[Path] = []
    child_tas: Set[Path] = set()

    # First look for TAs in direct children
    try:
        for child_path in base_path.iterdir():
            if child_path.is_dir() and is_valid_ta(child_path):
                child_tas.add(child_path)
    except (PermissionError, OSError):
        # Skip directories we can't access
        pass

    tas.extend(sorted(child_tas))  # Add sorted to ensure consistent ordering

    # If recursive, search subdirectories (excluding already found TAs)
    if recursive:
        try:
            for child_path in base_path.iterdir():
                if child_path.is_dir() and child_path not in child_tas:
                    try:
                        # Recursively search for TAs in subdirectories
                        child_results = find_tas(child_path, recursive=True)
                        tas.extend(child_results)
                    except (
                        FileNotFoundError,
                        NotADirectoryError,
                        PermissionError,
                        OSError,
                    ):
                        # Skip any subdirectories with access issues
                        continue
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass

    return tas
