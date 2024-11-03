"""Version management for Splunk TAs."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def read_ta_version(ta_path: Path) -> Optional[str]:
    """
    Read the version from a TA's app.conf file.

    Args:
        ta_path: Path to the TA directory

    Returns:
        str: Version string or None if not found
    """
    app_conf = ta_path / "default" / "app.conf"
    if not app_conf.exists():
        return None

    # Simple config parser to avoid external dependencies
    version = None
    try:
        with open(app_conf, "r") as f:
            in_launcher = False
            for line in f:
                line = line.strip()
                if line == "[launcher]":
                    in_launcher = True
                elif in_launcher and line.startswith("version"):
                    version = line.split("=")[1].strip()
                    break
    except Exception:
        return None

    return version


def update_ta_version(ta_path: Path, new_version: str) -> bool:
    """
    Update the version in a TA's app.conf file.

    Args:
        ta_path: Path to the TA directory
        new_version: New version string to set

    Returns:
        bool: True if successful, False otherwise
    """
    app_conf = ta_path / "default" / "app.conf"
    if not app_conf.exists():
        return False

    try:
        # Read current content
        with open(app_conf, "r") as f:
            lines = f.readlines()

        # Update version
        in_launcher = False
        for i, line in enumerate(lines):
            if line.strip() == "[launcher]":
                in_launcher = True
            elif in_launcher and line.strip().startswith("version"):
                lines[i] = f"version = {new_version}\n"
                break

        # Write back
        with open(app_conf, "w") as f:
            f.writelines(lines)

        return True
    except Exception:
        return False


def find_tas(base_path: Path) -> List[Path]:
    """
    Find all TAs in the given directory.

    Args:
        base_path: Base directory to search

    Returns:
        List[Path]: List of paths to TA directories
    """
    tas = []
    for path in base_path.iterdir():
        if path.is_dir() and path.name.startswith("TA-"):
            if (path / "default" / "app.conf").exists():
                tas.append(path)
    return tas
