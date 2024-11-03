"""Command-line interface for byDefault."""

import sys
from pathlib import Path
from typing import List, Optional

from bydefault.core import version_manager
from bydefault.core.splunk_ops import SplunkConfManager


def merge_command(path: Path) -> int:
    """
    Execute merge command for Splunk configurations.

    Args:
        path: Path to the TA directory

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    if not path.is_dir():
        print(f"Error: {path} is not a directory")
        return 1

    # Check if this is a TA directory (has default/app.conf)
    if not (path / "default" / "app.conf").exists():
        print("Error: Not a valid TA directory (missing default/app.conf)")
        return 1

    manager = SplunkConfManager(path)

    # Merge configuration files
    local_configs = manager.get_local_configs()
    if not local_configs:
        print("No local configuration files found")
        return 1

    success = True
    for conf_file in local_configs:
        merge_success, message = manager.merge_conf_files(conf_file)
        print(message)
        if not merge_success:
            success = False

    # Merge metadata if it exists
    if (path / "metadata" / "local.meta").exists():
        meta_success, message = manager.merge_meta()
        print(message)
        if not meta_success:
            success = False
    else:
        print("No local.meta file found, skipping metadata merge")

    return 0 if success else 1


def version_command(path: Path, new_version: str) -> int:
    """Execute version update command."""
    tas = version_manager.find_tas(path)
    if not tas:
        print("No TAs found in the current directory")
        return 1

    success = True
    for ta_path in tas:
        if version_manager.update_ta_version(ta_path, new_version):
            print(f"Updated version in {ta_path.name}")
        else:
            print(f"Failed to update version in {ta_path.name}")
            success = False

    return 0 if success else 1


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the byDefault CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("Usage: bydefault <command> [options]")
        print("\nCommands:")
        print("  merge     - Merge local configurations into default")
        print("  version   - Update version across all TAs")
        return 1

    command = args[0]
    current_path = Path.cwd()

    if command == "merge":
        return merge_command(current_path)
    elif command == "version":
        if len(args) < 2:
            print("Usage: bydefault version <new_version>")
            return 1
        return version_command(current_path, args[1])
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
