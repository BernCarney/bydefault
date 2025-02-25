"""Models for change detection and tracking in Splunk TAs.

This module defines the data structures for tracking changes between local and default
configurations in Splunk Technology Add-ons. It's used by the scan command to detect,
organize, and report configuration changes.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class ChangeType(Enum):
    """Types of detected changes between configuration files.

    Used to categorize changes at both stanza and setting levels.

    Args:
        ADDED: New stanza or setting only in local configuration
        MODIFIED: Setting exists in both but with different values
        REMOVED: Setting or stanza exists in default but not in local
    """

    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"


@dataclass
class SettingChange:
    """Represents a change to a specific configuration setting.

    Args:
        name: Name of the setting (key)
        change_type: Type of change (added, modified, removed)
        local_value: Value in local configuration (None if removed)
        default_value: Value in default configuration (None if added)
    """

    name: str
    change_type: ChangeType
    local_value: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class StanzaChange:
    """Represents changes to a specific stanza in a configuration file.

    Args:
        name: Name of the stanza including brackets (e.g., "[stanza_name]")
        change_type: Type of change (added, modified, removed)
        settings: Dictionary mapping setting names to their change types
        setting_changes: Detailed information about each changed setting
    """

    name: str
    change_type: ChangeType
    settings: Dict[str, ChangeType] = field(default_factory=dict)
    setting_changes: List[SettingChange] = field(default_factory=list)

    def add_setting_change(
        self,
        name: str,
        change_type: ChangeType,
        local_value: Optional[str] = None,
        default_value: Optional[str] = None,
    ) -> None:
        """Add a setting change to this stanza.

        Args:
            name: Name of the setting
            change_type: Type of change
            local_value: Value in local configuration
            default_value: Value in default configuration
        """
        self.settings[name] = change_type
        self.setting_changes.append(
            SettingChange(
                name=name,
                change_type=change_type,
                local_value=local_value,
                default_value=default_value,
            )
        )


@dataclass
class FileChange:
    """Represents changes to a configuration file.

    Args:
        file_path: Relative path to the file within the TA
        stanza_changes: List of changes to stanzas in this file
        is_new: Whether this file only exists in local
    """

    file_path: Path
    stanza_changes: List[StanzaChange] = field(default_factory=list)
    is_new: bool = False

    @property
    def has_changes(self) -> bool:
        """Whether this file has any changes.

        Returns:
            bool: True if there are any stanza changes, False otherwise
        """
        return bool(self.stanza_changes)


@dataclass
class ScanResult:
    """Results from scanning a TA directory for configuration changes.

    Args:
        ta_path: Path to the TA directory
        file_changes: List of file changes detected
        is_valid_ta: Whether the directory is a valid TA
        error_message: Error message if scanning failed
    """

    ta_path: Path
    file_changes: List[FileChange] = field(default_factory=list)
    is_valid_ta: bool = True
    error_message: Optional[str] = None

    @property
    def has_changes(self) -> bool:
        """Whether this TA has any changes.

        Returns:
            bool: True if there are any file changes, False otherwise
        """
        return any(fc.has_changes for fc in self.file_changes)
