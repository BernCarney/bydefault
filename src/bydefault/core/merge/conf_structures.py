"""Structural definitions for Splunk configuration files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass(frozen=True)
class ConfValue:
    """Single configuration value with its metadata."""

    value: str
    is_continued: bool = False


@dataclass
class ConfStanza:
    """
    Single stanza in a .conf file.

    A stanza contains a collection of key-value pairs (settings) and
    maintains its position in the file via line number.
    """

    name: str
    settings: Dict[str, ConfValue] = field(default_factory=dict)
    line_number: int = 0

    def __post_init__(self) -> None:
        """Validate stanza structure."""
        if not (self.name.startswith("[") and self.name.endswith("]")):
            raise ValueError(f"Invalid stanza format: {self.name}")

    def add_setting(
        self,
        key: str,
        value: str,
        position: str = "end",
        conf_file: Optional["ConfFile"] = None,
    ) -> None:
        """
        Add a setting to the stanza.

        Args:
            key: Setting key
            value: Setting value
            position: Where to add the setting ('start' or 'end', defaults to 'end')
            conf_file: Optional parent ConfFile for line number calculation

        Raises:
            ValueError: If position is invalid
        """
        # Simple append if no conf_file provided
        if conf_file is None:
            self.settings[key] = ConfValue(value)
            return

        # Get stanza's lines in the file
        stanza_start = next(
            i
            for i, line in enumerate(conf_file.lines)
            if isinstance(line.content, ConfStanza) and line.content == self
        )
        stanza_end = next(
            (
                i
                for i, line in enumerate(
                    conf_file.lines[stanza_start + 1 :], start=stanza_start + 1
                )
                if isinstance(line.content, ConfStanza)
            ),
            len(conf_file.lines),
        )
        stanza_lines = conf_file.lines[stanza_start:stanza_end]

        # Calculate new line number
        line_number = ConfLine.calculate_line_number(stanza_lines, position)

        # Add the new line
        conf_value = ConfValue(value)
        new_line = ConfLine(number=line_number, content=conf_value)

        # Insert at the correct position
        insert_pos = stanza_start + 1 if position == "start" else stanza_end
        conf_file.lines.insert(insert_pos, new_line)

        # Update line numbers for subsequent lines
        for line in conf_file.lines[insert_pos + 1 :]:
            line.number += 1

    @property
    def is_default_stanza(self) -> bool:
        """Check if this is the [default] stanza."""
        return self.name == "[default]"


@dataclass
class ConfLine:
    """Represents a single line in the configuration file."""

    number: int
    content: Optional[Union[ConfValue, ConfStanza]] = None
    is_blank: bool = False
    is_comment: bool = False
    comment_text: Optional[str] = None

    @staticmethod
    def calculate_line_number(lines: List["ConfLine"], position: str = "end") -> int:
        """
        Calculate appropriate line number based on position.

        Args:
            lines: List of existing lines
            position: Where to add the line ('start' or 'end', defaults to 'end')

        Returns:
            Calculated line number

        Raises:
            ValueError: If position is invalid
        """
        if not lines:
            return 1

        if position == "start":
            return lines[0].number - 1 if lines[0].number > 1 else 1
        elif position == "end":
            return lines[-1].number + 1
        else:
            raise ValueError(f"Invalid position: {position}. Must be 'start' or 'end'")


@dataclass
class ConfFile:
    """
    Represents a complete .conf file.

    A .conf file is a collection of stanzas, where each stanza contains
    settings. The file maintains its stanzas in order and provides methods
    to access and manipulate them.
    """

    path: Path
    lines: List[ConfLine] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate file structure."""
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        if self.path.suffix != ".conf":
            raise ValueError(f"Not a .conf file: {self.path}")

    def add_line(
        self,
        number: int,
        content: Optional[Union[ConfValue, ConfStanza]] = None,
        *,  # Force keyword arguments after this
        is_blank: bool = False,
        is_comment: Optional[bool] = None,
        comment_text: Optional[str] = None,
    ) -> ConfLine:
        """
        Add a line to the file with automatic validation.

        Args:
            number: Line number
            content: Optional content (ConfValue or ConfStanza)
            is_blank: Whether this is a blank line (default: False)
            is_comment: Whether this is a comment line (automatically set if comment_text provided)
            comment_text: Text of the comment if this is a comment line

        Returns:
            The created ConfLine

        Raises:
            ValueError: If line number is invalid or not sequential
        """
        if number <= 0:
            raise ValueError("Line numbers must be positive")
        if self.lines and number <= self.lines[-1].number:
            raise ValueError(f"Line number {number} is not sequential")

        # Automatically set is_comment if comment_text is provided
        if is_comment is None:
            is_comment = bool(comment_text)

        line = ConfLine(
            number=number,
            content=content,
            is_blank=is_blank,
            is_comment=is_comment,
            comment_text=comment_text,
        )
        self.lines.append(line)
        return line

    @property
    def stanzas(self) -> List[ConfStanza]:
        """Get all stanzas in order."""
        return [
            line.content for line in self.lines if isinstance(line.content, ConfStanza)
        ]

    def add_stanza(self, name: str, line_number: int) -> ConfStanza:
        """Create and add a new stanza."""
        stanza = ConfStanza(name, line_number=line_number)
        self.stanzas.append(stanza)
        return stanza

    def get_stanza(self, name: str) -> Optional[ConfStanza]:
        """Get a stanza by name."""
        return next((s for s in self.stanzas if s.name == name), None)

    @property
    def default_stanza(self) -> Optional[ConfStanza]:
        """Get the [default] stanza if it exists."""
        return self.get_stanza("[default]")

    def add_setting_to_stanza(
        self, stanza_name: str, key: str, value: str, position: str = "end"
    ) -> None:
        """
        Add a setting to a specific stanza with automatic line number calculation.

        Args:
            stanza_name: Name of the stanza to add to
            key: Setting key
            value: Setting value
            position: Where to add the setting ('start' or 'end', defaults to 'end')

        Raises:
            ValueError: If stanza not found or position is invalid
        """
        stanza = next(
            (
                line.content
                for line in self.lines
                if isinstance(line.content, ConfStanza)
                and line.content.name == stanza_name
            ),
            None,
        )
        if not stanza:
            raise ValueError(f"Stanza not found: {stanza_name}")

        stanza.add_setting(key, value, position, self)
