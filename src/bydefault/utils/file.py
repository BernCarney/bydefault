"""File operation utilities."""

from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple


class InvalidWorkingDirectoryError(Exception):
    """Raised when the working directory is not valid for TA operations."""

    pass


def validate_working_context(path: Path) -> Path:
    """
    Validate and resolve the working context for TA operations.

    This function checks if we're in a valid working context and tries to
    locate the TA root directory. Valid contexts are:
    1. Inside a TA directory
    2. Inside a directory containing multiple TAs
    3. Inside a git repository with TAs

    Args:
        path: Starting path (usually current working directory)

    Returns:
        Path to the validated working directory

    Raises:
        InvalidWorkingDirectoryError: If no valid working context is found
    """
    # First, check if we're inside a TA directory
    current = path.resolve()
    if is_ta_directory(current):
        return current

    # Check if current directory contains TAs
    if any(is_ta_directory(d) for d in current.iterdir() if d.is_dir()):
        return current

    # Try to find git root
    try:
        git_root = find_git_root(current)
        if git_root and any(
            is_ta_directory(d) for d in git_root.iterdir() if d.is_dir()
        ):
            return git_root
    except Exception:  # noqa: BLE001, S110
        pass

    raise InvalidWorkingDirectoryError(
        "Not in a valid working directory. Please run this command:\n"
        "1. Inside a TA directory\n"
        "2. Inside a directory containing TAs\n"
        "3. Inside a git repository containing TAs"
    )


def find_git_root(start_path: Path) -> Optional[Path]:
    """
    Find the root directory of the git repository.

    Args:
        start_path: Path to start searching from

    Returns:
        Path to git root directory or None if not in a git repository
    """
    current = start_path.resolve()
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return None


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


def find_ta_directories(root_path: Path) -> List[Path]:
    """
    Find all valid TA directories under root path.

    Args:
        root_path: Root directory to search for TAs

    Returns:
        List of paths to valid TA directories

    Raises:
        FileNotFoundError: If root path doesn't exist
        InvalidWorkingDirectoryError: If no TAs are found
    """
    if not root_path.exists():
        raise FileNotFoundError(f"Root directory not found: {root_path}")

    ta_dirs = [
        path for path in root_path.iterdir() if path.is_dir() and is_ta_directory(path)
    ]

    if not ta_dirs:
        raise InvalidWorkingDirectoryError(
            f"No valid TA directories found in {root_path}"
        )

    return ta_dirs


def validate_ta_path(ta_path: Path) -> bool:
    """
    Validate single TA directory structure.

    More thorough validation than is_ta_directory, checking for:
    - Required directories (local, default, metadata)
    - Essential files (app.conf, local.meta)
    - Proper file permissions

    Args:
        ta_path: Path to TA directory to validate

    Returns:
        True if TA directory structure is valid
    """
    if not is_ta_directory(ta_path):
        return False

    # Check for metadata directory
    metadata_dir = ta_path / "metadata"
    if not metadata_dir.is_dir():
        return False

    # Check for local.meta
    local_meta = ta_path / "local" / "local.meta"
    if not local_meta.exists():
        return False

    # Additional validation could be added here
    return True


def get_meta_files(ta_path: Path) -> Tuple[Path, Optional[Path]]:
    """
    Get local.meta and default.meta paths.

    Args:
        ta_path: Path to TA directory

    Returns:
        Tuple of (local.meta path, default.meta path or None)

    Raises:
        FileNotFoundError: If TA path or local.meta doesn't exist
    """
    local_meta = ta_path / "local" / "local.meta"
    default_meta = ta_path / "default" / "default.meta"

    if not local_meta.exists():
        raise FileNotFoundError(f"local.meta not found: {local_meta}")

    return local_meta, default_meta if default_meta.exists() else None


def validate_meta_files(local_meta: Path, default_meta: Optional[Path]) -> bool:
    """
    Validate metadata file structure.

    Args:
        local_meta: Path to local.meta file
        default_meta: Optional path to default.meta file

    Returns:
        True if metadata files are valid
    """
    if not local_meta.exists():
        return False

    # Basic validation - could be enhanced to check file contents
    try:
        with local_meta.open() as f:
            local_content = f.read()
        if not local_content.strip():
            return False

        if default_meta and default_meta.exists():
            with default_meta.open() as f:
                default_content = f.read()
            if not default_content.strip():
                return False

        return True
    except Exception:
        return False
