"""Models for merge command functionality.

This module defines the data structures used by the merge command to track
and process configuration changes between local and default directories.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from bydefault.models.sort_models import StanzaType


class MergeMode(Enum):
    """Available merge modes."""

    MERGE = "merge"  # Combine local and default, preferring local values
    REPLACE = "replace"  # Complete replacement of default stanzas with local ones


@dataclass
class StanzaMergeResult:
    """Results from merging a single stanza."""

    name: str
    type: StanzaType
    is_new: bool = False
    settings_added: Set[str] = field(default_factory=set)
    settings_updated: Set[str] = field(default_factory=set)
    settings_preserved: Set[str] = field(default_factory=set)
    comments_merged: bool = False
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether the merge was successful."""
        return self.error is None


@dataclass
class FileMergeResult:
    """Results from merging a single configuration file."""

    file_path: Path
    new_stanzas: Set[str] = field(default_factory=set)
    merged_stanzas: Set[str] = field(default_factory=set)
    preserved_stanzas: Set[str] = field(default_factory=set)
    stanza_results: Dict[str, StanzaMergeResult] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether the merge was successful."""
        return self.error is None and all(
            result.success for result in self.stanza_results.values()
        )


@dataclass
class MergeResult:
    """Overall results from a merge operation."""

    file_results: List[FileMergeResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Whether the merge was successful."""
        return self.error is None and all(
            result.success for result in self.file_results
        )

    def add_file_result(self, result: FileMergeResult) -> None:
        """Add a file merge result.

        Args:
            result: File merge result to add
        """
        self.file_results.append(result)
