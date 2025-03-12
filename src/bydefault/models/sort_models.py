"""Data models for sorting operations.

This module contains data models for the sorting operations used by
the sort command.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


class StanzaType(Enum):
    """Enum for stanza classification types.

    This enum defines the types of stanzas for sorting purposes.
    """

    GLOBAL = (
        auto()
    )  # Global settings with no stanza header (settings at the top of the file)
    EMPTY_STANZA = auto()  # Empty stanza [] - another form of global settings
    STAR_STANZA = auto()  # Star stanza [*] - another form of global settings
    DEFAULT = auto()  # Default stanza [default]
    APP_SPECIFIC = (
        auto()
    )  # App-specific stanzas with no type specifier (e.g., [perfmon], [sourcetype])
    GLOBAL_WILDCARD = auto()  # Global wildcard stanzas [*::attribute]
    TYPE_WILDCARD = auto()  # Type wildcard stanzas [type::*]
    TYPE_WILDCARD_PREFIX = auto()  # Type wildcard prefix stanzas [type::*-attribute]
    TYPE_SPECIFIC = auto()  # Type specific stanzas [type::attribute]


@dataclass
class Comment:
    """A comment in a configuration file.

    Attributes:
        content: The content of the comment
        line_number: The line number of the comment
        associated_with: What the comment is associated with (stanza or setting)
    """

    content: str
    line_number: int
    associated_with: Optional[str] = None


@dataclass
class Setting:
    """A key-value setting in a configuration file.

    Attributes:
        key: The key
        value: The value
        line_number: The line number of the setting
        comments: Comments associated with this setting
    """

    key: str
    value: str
    line_number: int
    comments: List[Comment] = field(default_factory=list)


@dataclass
class Stanza:
    """A stanza in a configuration file.

    Attributes:
        name: The name of the stanza
        type: The type of the stanza
        line_number: The line number of the stanza
        settings: Settings in this stanza
        comments: Comments associated with this stanza
        blank_lines_after: Number of blank lines after this stanza
    """

    name: str
    type: StanzaType
    line_number: int
    settings: Dict[str, Setting] = field(default_factory=dict)
    comments: List[Comment] = field(default_factory=list)
    blank_lines_after: int = 1


@dataclass
class SortResult:
    """Result of a sort operation.

    Attributes:
        stanzas_reordered: Number of stanzas reordered
        settings_sorted: Number of settings sorted
        comments_preserved: Number of comments preserved
        global_settings_count: Number of global settings
        default_stanza_found: Whether a default stanza was found
        default_stanza_position: Position of the default stanza
        wildcard_stanzas: Wildcard stanzas and their positions
        specific_stanzas_groups: Groups of specific stanzas
    """

    stanzas_reordered: int = 0
    settings_sorted: int = 0
    comments_preserved: int = 0
    global_settings_count: int = 0
    default_stanza_found: bool = False
    default_stanza_position: int = 0
    wildcard_stanzas: Dict[str, int] = field(default_factory=dict)
    specific_stanzas_groups: List[str] = field(default_factory=list)
