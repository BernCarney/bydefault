"""
Change detection module for Splunk TA files.

This module implements the logic to detect changes between Splunk TA files,
focusing on configuration files and stanza changes.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from bydefault.models.change_detection import (
    ChangeType,
    FileChange,
    ScanResult,
    StanzaChange,
)


def detect_file_changes(
    base_path: Path, current_path: Optional[Path] = None
) -> List[FileChange]:
    """
    Detect changes between files in base_path and current_path.
    If current_path is None, only report files in base_path as new.

    Args:
        base_path: Path to the base TA directory
        current_path: Path to the current TA directory (optional)

    Returns:
        List of FileChange objects representing changes detected
    """
    if not base_path.is_dir():
        raise ValueError(f"Base path {base_path} must be a directory")

    if current_path and not current_path.is_dir():
        raise ValueError(f"Current path {current_path} must be a directory")

    changes = []

    # Get all .conf files from base path (recursively)
    base_files = _get_conf_files(base_path)

    if current_path:
        # Get all .conf files from current path (recursively)
        current_files = _get_conf_files(current_path)

        # Find added files (in current but not in base)
        for rel_path in current_files - base_files:
            current_file = current_path / rel_path
            changes.append(
                FileChange(
                    file_path=rel_path,
                    stanza_changes=[],
                    is_new=True,
                )
            )

        # Find removed files (in base but not in current)
        for rel_path in base_files - current_files:
            # For removed files, we just note them - we don't need to check
            # binary status
            changes.append(
                FileChange(
                    file_path=rel_path,
                    stanza_changes=[],
                    is_new=False,  # Not a new file, it's a removed one
                )
            )

        # Find modified files (in both but with changes)
        for rel_path in base_files & current_files:
            base_file = base_path / rel_path
            current_file = current_path / rel_path

            if _is_binary_file(base_file) or _is_binary_file(current_file):
                # For binary files, just check if they're different
                if not _files_are_identical(base_file, current_file):
                    changes.append(
                        FileChange(
                            file_path=rel_path,
                            stanza_changes=[],
                            is_new=False,
                        )
                    )
            else:
                # For text config files, check stanza changes
                stanza_changes = detect_stanza_changes(base_file, current_file)
                if stanza_changes:
                    changes.append(
                        FileChange(
                            file_path=rel_path,
                            stanza_changes=stanza_changes,
                            is_new=False,
                        )
                    )
    else:
        # If no current_path, mark all base files as new
        for rel_path in base_files:
            base_file = base_path / rel_path
            changes.append(
                FileChange(
                    file_path=rel_path,
                    stanza_changes=[],
                    is_new=True,
                )
            )

    return changes


def detect_stanza_changes(base_file: Path, current_file: Path) -> List[StanzaChange]:
    """
    Detect changes between stanzas in base_file and current_file.

    Args:
        base_file: Path to the base file
        current_file: Path to the current file

    Returns:
        List of StanzaChange objects representing changes detected
    """
    # Parse both files into dictionaries of stanzas and their properties
    base_stanzas = _parse_conf_file(base_file)
    current_stanzas = _parse_conf_file(current_file)

    changes = []

    # Find added stanzas (in current but not in base)
    for stanza_name in current_stanzas.keys() - base_stanzas.keys():
        # Create a StanzaChange for the added stanza
        stanza_change = StanzaChange(
            name=stanza_name,
            change_type=ChangeType.ADDED,
        )

        # Add setting changes for each setting in the stanza
        for setting_name, setting_value in current_stanzas[stanza_name].items():
            stanza_change.add_setting_change(
                name=setting_name,
                change_type=ChangeType.ADDED,
                local_value=setting_value,
                default_value=None,
            )

        changes.append(stanza_change)

    # Find removed stanzas (in base but not in current)
    for stanza_name in base_stanzas.keys() - current_stanzas.keys():
        # Create a StanzaChange for the removed stanza
        stanza_change = StanzaChange(
            name=stanza_name,
            change_type=ChangeType.REMOVED,
        )

        # Add setting changes for each setting in the stanza
        for setting_name, setting_value in base_stanzas[stanza_name].items():
            stanza_change.add_setting_change(
                name=setting_name,
                change_type=ChangeType.REMOVED,
                local_value=None,
                default_value=setting_value,
            )

        changes.append(stanza_change)

    # Find modified stanzas (in both but with changes)
    for stanza_name in base_stanzas.keys() & current_stanzas.keys():
        base_properties = base_stanzas[stanza_name]
        current_properties = current_stanzas[stanza_name]

        # Check if properties are different
        if base_properties != current_properties:
            stanza_change = StanzaChange(
                name=stanza_name,
                change_type=ChangeType.MODIFIED,
            )

            # Find added properties
            for setting_name in current_properties.keys() - base_properties.keys():
                stanza_change.add_setting_change(
                    name=setting_name,
                    change_type=ChangeType.ADDED,
                    local_value=current_properties[setting_name],
                    default_value=None,
                )

            # Find removed properties
            for setting_name in base_properties.keys() - current_properties.keys():
                stanza_change.add_setting_change(
                    name=setting_name,
                    change_type=ChangeType.REMOVED,
                    local_value=None,
                    default_value=base_properties[setting_name],
                )

            # Find modified properties
            for setting_name in base_properties.keys() & current_properties.keys():
                if base_properties[setting_name] != current_properties[setting_name]:
                    stanza_change.add_setting_change(
                        name=setting_name,
                        change_type=ChangeType.MODIFIED,
                        local_value=current_properties[setting_name],
                        default_value=base_properties[setting_name],
                    )

            changes.append(stanza_change)

    return changes


def _get_conf_files(dir_path: Path) -> Set[Path]:
    """
    Get all .conf files from a directory (recursively).
    Returns paths relative to the input directory.

    Args:
        dir_path: Directory to search for .conf files

    Returns:
        Set of Path objects representing .conf files, relative to dir_path
    """
    conf_files = set()

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".conf"):
                # Get path relative to dir_path
                rel_path = Path(os.path.relpath(Path(root) / file, dir_path))
                conf_files.add(rel_path)

    return conf_files


def _is_stanza_header(line: str, previous_line: Optional[str] = None) -> bool:
    """
    Determine if a line represents a legitimate stanza header in Splunk conf files.

    Args:
        line: String line to check
        previous_line: The previous line for continuation context

    Returns:
        bool: True if line is a stanza header, False otherwise
    """
    # Basic stanza format check
    stripped = line.strip()
    if not (stripped.startswith("[") and stripped.endswith("]")):
        return False

    # Check if previous line ends with continuation character
    if previous_line and previous_line.strip().endswith("\\"):
        return False

    # Exclude lines that appear to be part of a command context
    command_patterns = [
        "| foreach",
        "| map",
        "| search",
        "| where",
        "| eval",
        "| append",
        "| join",
        "| stats",
        "| sort",
    ]

    for pattern in command_patterns:
        if pattern in stripped:
            return False

    # Typically genuine stanza headers don't have specific characters in them
    stanza_content = stripped[1:-1]  # Extract content between brackets
    if "|" in stanza_content or "(" in stanza_content or ")" in stanza_content:
        return False

    return True


def _parse_conf_file(file_path: Path) -> Dict[str, Dict[str, str]]:
    """
    Parse a .conf file into a dictionary of stanzas and their properties.

    Args:
        file_path: Path to the .conf file

    Returns:
        Dictionary of stanza names to dictionaries of property names and values
    """
    # Process the file as a single string to handle multiline values properly
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Initialize the result
    stanzas = {}
    current_stanza = None
    lines = content.splitlines()

    # First pass: Identify genuine stanza headers
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith(("#", ";")):
            i += 1
            continue

        # Check for stanza header using the helper function
        prev_line = lines[i - 1].strip() if i > 0 else None
        if _is_stanza_header(line, prev_line):
            # Only treat as stanza if it's not part of a command
            current_stanza = line[1:-1]  # Remove brackets
            stanzas[current_stanza] = {}
            i += 1
            continue

        # Handle key-value pairs, including multiline values
        if current_stanza is not None and "=" in line:
            parts = line.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip()

            # Check if this is a multiline value
            if value.endswith("\\"):
                # Start of a multiline value - collect all lines until we find
                # one that doesn't end with \
                multiline_value = value
                j = i + 1

                while (
                    j < len(lines)
                    and lines[j].strip()
                    and not _is_stanza_header(
                        lines[j].strip(), lines[j - 1] if j > 0 else None
                    )
                ):
                    next_line = lines[j].strip()

                    # If the previous line ended with \, remove it and append this line
                    if multiline_value.endswith("\\"):
                        multiline_value = multiline_value[:-1] + " " + next_line
                    else:
                        multiline_value += " " + next_line

                    # If this line doesn't end with \, we're done with this
                    # multiline value
                    if not next_line.endswith("\\"):
                        break

                    j += 1

                # Store the complete multiline value
                stanzas[current_stanza][key] = multiline_value

                # Skip the lines we've processed
                i = j + 1
                continue
            else:
                # Simple key-value pair
                stanzas[current_stanza][key] = value

        i += 1

    return stanzas


def _is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary by looking at the first few thousand bytes.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file appears to be binary, False otherwise
    """
    try:
        chunk_size = 4096
        with open(file_path, "rb") as f:
            chunk = f.read(chunk_size)
            return b"\0" in chunk  # A simple heuristic - presence of null bytes
    except Exception:
        # If we can't read the file, assume it's not binary
        return False


def _files_are_identical(file1: Path, file2: Path) -> bool:
    """
    Check if two files are identical by comparing their contents.

    Args:
        file1: Path to the first file
        file2: Path to the second file

    Returns:
        True if the files are identical, False otherwise
    """
    if file1.stat().st_size != file2.stat().st_size:
        return False

    # For smaller files, compare them directly
    if file1.stat().st_size < 10 * 1024 * 1024:  # 10 MB
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            return f1.read() == f2.read()

    # For larger files, read in chunks
    chunk_size = 4096
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        while True:
            chunk1 = f1.read(chunk_size)
            chunk2 = f2.read(chunk_size)

            if chunk1 != chunk2:
                return False

            if not chunk1:  # End of both files
                return True


def scan_directory(ta_path: Path, baseline_path: Optional[Path] = None) -> ScanResult:
    """
    Scan a TA directory for changes between local and default directories.
    If a baseline_path is provided (advanced use case), compare the TA against
    the baseline instead.

    Args:
        ta_path: Path to the TA directory to scan
        baseline_path: Optional path to a baseline TA directory to compare against
            (advanced use case)

    Returns:
        ScanResult object containing information about changes detected
    """
    if not ta_path.is_dir():
        raise ValueError(f"TA path {ta_path} must be a directory")

    # Check for local and default directories in the TA
    local_dir = ta_path / "local"
    default_dir = ta_path / "default"

    if not default_dir.is_dir():
        raise ValueError(f"TA path {ta_path} does not have a default directory")

    if baseline_path:
        # Advanced use case: compare against baseline
        file_changes = detect_file_changes(baseline_path, ta_path)
        return ScanResult(
            ta_path=ta_path,
            file_changes=file_changes,
            is_valid_ta=True,
        )
    elif local_dir.is_dir():
        # Standard use case: compare local vs default
        file_changes = detect_file_changes(default_dir, local_dir)
        return ScanResult(
            ta_path=ta_path,
            file_changes=file_changes,
            is_valid_ta=True,
        )
    else:
        # No local directory, so no changes to report
        return ScanResult(
            ta_path=ta_path,
            file_changes=[],
            is_valid_ta=True,
        )
