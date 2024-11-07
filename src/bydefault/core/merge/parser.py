"""Parser for Splunk configuration values."""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedValue:
    """Result of parsing a configuration value."""

    value: str
    continuation_lines: List[str]
    inline_comment: Optional[str] = None


class ConfValueParser:
    """Parser for configuration values with continuation support."""

    # Raw string for better readability
    CONTINUATION_PATTERN = r"^(.*?)\\[ \t]*(?:#(.*))?$"  # Non-greedy match for value
    INLINE_COMMENT_PATTERN = r"^(.*?)[ \t]*#(.*)$"  # Non-greedy match before comment
    ESCAPED_BACKSLASH = r"\\{2}"

    @classmethod
    def parse(cls, initial_line: str, following_lines: List[str] = None) -> ParsedValue:
        """
        Parse a configuration value that may span multiple lines.

        Args:
            initial_line: The first line of the value
            following_lines: Additional lines that may be continuations

        Returns:
            ParsedValue containing the complete value and any comments

        Example:
            >>> parser = ConfValueParser()
            >>> result = parser.parse("value1 \\ ", ["    value2"])
            >>> assert result.value == "value1 value2"
        """
        following_lines = following_lines or []
        value_parts = []
        continuation_lines = []
        inline_comment = None

        # Process initial line
        if match := re.match(cls.CONTINUATION_PATTERN, initial_line):
            # Line ends with backslash
            value_parts.append(match.group(1).rstrip())
            if comment := match.group(2):
                inline_comment = comment.strip()
        elif match := re.match(cls.INLINE_COMMENT_PATTERN, initial_line):
            # Line has inline comment
            value_parts.append(match.group(1).rstrip())
            inline_comment = match.group(2).strip()
        else:
            # Handle escaped backslashes before adding value
            line = re.sub(cls.ESCAPED_BACKSLASH, r"\\", initial_line)
            value_parts.append(line.rstrip())

        # Process continuation lines
        for line in following_lines:
            continuation_lines.append(line)
            stripped = line.lstrip()
            if not stripped:  # Skip empty lines
                continue
            if match := re.match(cls.CONTINUATION_PATTERN, stripped):
                value_parts.append(match.group(1).rstrip())
                if comment := match.group(2):
                    inline_comment = comment.strip()
            elif match := re.match(cls.INLINE_COMMENT_PATTERN, stripped):
                value_parts.append(match.group(1).rstrip())
                inline_comment = match.group(2).strip()
            else:
                value_parts.append(stripped.rstrip())

        # Filter out empty strings before joining
        value_parts = [part for part in value_parts if part]
        
        return ParsedValue(
            value=" ".join(value_parts),
            continuation_lines=continuation_lines,
            inline_comment=inline_comment,
        )
