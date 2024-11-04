"""File operation utilities."""

from pathlib import Path
from typing import Dict, Iterator, List, Optional


def find_conf_files(path: Path, pattern: str = "*.conf") -> Iterator[Path]:
    """
    Find all .conf files in the given path.

    Args:
        path: Directory path to search
        pattern: File pattern to match (default: "*.conf")

    Returns:
        Iterator of Path objects for matching files

    Raises:
        FileNotFoundError: If path doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    return path.rglob(pattern)


def get_local_conf_files(ta_path: Path) -> List[Path]:
    """
    Get all .conf files in the local directory of a TA.

    Args:
        ta_path: Path to the TA directory

    Returns:
        List of paths to .conf files in local/

    Raises:
        FileNotFoundError: If TA path or local directory doesn't exist
    """
    local_dir = ta_path / "local"
    if not local_dir.exists():
        raise FileNotFoundError(f"Local directory not found: {local_dir}")
    return list(find_conf_files(local_dir))


def match_conf_files(ta_path: Path) -> Dict[Path, Optional[Path]]:
    """
    Match .conf files between local/ and default/ directories.

    Args:
        ta_path: Path to the TA directory

    Returns:
        Dictionary mapping local .conf files to their default counterparts
        (None if no default file exists)

    Raises:
        FileNotFoundError: If TA path doesn't exist
    """
    if not ta_path.exists():
        raise FileNotFoundError(f"TA directory not found: {ta_path}")

    local_files = get_local_conf_files(ta_path)
    result = {}

    for local_file in local_files:
        # Get corresponding default file path
        default_file = ta_path / "default" / local_file.name
        result[local_file] = default_file if default_file.exists() else None

    return result


def is_ta_directory(path: Path) -> bool:
    """
    Check if a directory is a valid Splunk TA directory.

    Args:
        path: Directory path to check

    Returns:
        True if directory has the expected TA structure
    """
    return (
        path.is_dir()
        and (path / "default").is_dir()
        and (path / "local").is_dir()
        and (path / "default" / "app.conf").exists()
    )
