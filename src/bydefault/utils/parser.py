"""Parser for Splunk configuration files that preserves comments.

This module provides a parser for Splunk configuration files that
preserves comment relationships to stanzas and settings.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from bydefault.models.sort_models import Comment, Setting, Stanza, StanzaType


class CommentAwareParser:
    """Parser that preserves comment relationships to stanzas and settings.

    This class parses Splunk configuration files and preserves comment
    relationships to stanzas and settings.

    Attributes:
        file_path: The path to the configuration file
    """

    # Regular expressions for parsing
    STANZA_PATTERN = re.compile(r"^\s*\[(.*?)\]\s*$")
    SETTING_PATTERN = re.compile(r"^\s*([^=\s]+)\s*=\s*(.*?)(?:\s*#.*)?$")
    COMMENT_PATTERN = re.compile(r"^\s*#\s*(.*)\s*$")
    BLANK_LINE_PATTERN = re.compile(r"^\s*$")

    def __init__(self, file_path: Path):
        """Initialize the parser.

        Args:
            file_path: The path to the configuration file
        """
        self.file_path = file_path
        self.current_stanza: Optional[Stanza] = None
        self.stanzas: Dict[str, Stanza] = {}
        self.global_settings: Dict[str, Setting] = {}
        self.pending_comments: List[Comment] = []

    def parse(self):
        """Parse the configuration file.

        Returns:
            ParseResult: The parsed result containing stanzas and settings.
        """
        try:
            stanzas = {}
            global_settings = {}
            comments_buffer = []
            current_stanza = None
            continued_line = False
            continued_value = ""
            continued_key = ""
            continued_line_num = 0

            # For debugging
            stanza_types = {}

            with open(self.file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.rstrip("\n")

                    # Skip empty lines
                    if not line.strip():
                        continue

                    # Handle comments, unless we're in a continued line
                    if line.strip().startswith("#") and not continued_line:
                        comment = Comment(
                            content=line.strip(),
                            line_number=line_num,
                        )
                        comments_buffer.append(comment)
                        continue

                    # Handle stanza headers - [stanza_name], unless we're in a continued line
                    if (
                        not continued_line
                        and line.strip().startswith("[")
                        and line.strip().endswith("]")
                    ):
                        # Extract the stanza name without brackets
                        stanza_name = line.strip()[1:-1]

                        # Classify the stanza type
                        stanza_type = self._classify_stanza(stanza_name)

                        # For debugging
                        stanza_types[stanza_name] = stanza_type

                        # Create a new stanza
                        stanza = Stanza(
                            name=stanza_name,
                            type=stanza_type,
                            line_number=line_num,
                        )

                        # Associate any pending comments with this stanza
                        for comment in comments_buffer:
                            comment.associated_with = stanza_name
                            stanza.comments.append(comment)
                        comments_buffer = []

                        stanzas[stanza_name] = stanza
                        current_stanza = stanza
                        continue

                    # Check if we're continuing a previous line
                    if continued_line:
                        # Append this line to the continued value
                        continued_value += "\n" + line

                        # Check if this line continues
                        if line.rstrip().endswith("\\"):
                            # Remove the trailing backslash for display but keep continuing
                            continued_value = continued_value.rstrip("\\").rstrip()
                        else:
                            # End of continuation - create the setting
                            setting = Setting(
                                key=continued_key,
                                value=continued_value,
                                line_number=continued_line_num,
                            )

                            # Associate comments with this setting
                            if comments_buffer:
                                setting.comments.extend(comments_buffer)
                                comments_buffer = []

                            if current_stanza:
                                current_stanza.settings[continued_key] = setting
                            else:
                                global_settings[continued_key] = setting

                            # Reset continuation
                            continued_line = False
                            continued_value = ""
                            continued_key = ""
                        continue

                    # Check for settings
                    setting_match = self.SETTING_PATTERN.match(line)
                    if setting_match:
                        key = setting_match.group(1)
                        value = setting_match.group(2)

                        # Check if the line continues
                        if value.rstrip().endswith("\\"):
                            # Start collecting a multi-line value
                            continued_line = True
                            continued_key = key
                            continued_value = value.rstrip("\\").rstrip()
                            continued_line_num = line_num
                        else:
                            # Regular single-line setting
                            setting = Setting(
                                key=key, value=value, line_number=line_num
                            )

                            # Associate pending comments with this setting
                            if comments_buffer:
                                setting.comments.extend(comments_buffer)
                                comments_buffer = []

                            if current_stanza:
                                current_stanza.settings[key] = setting
                            else:
                                global_settings[key] = setting

            # For debugging
            print("Stanza Types:")
            for name, typ in stanza_types.items():
                print(f"  {name}: {typ}")

            return stanzas, global_settings

        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            raise e

    def _classify_stanza(self, stanza_name: str) -> StanzaType:
        """Classify a stanza based on its name.

        Args:
            stanza_name: The name of the stanza

        Returns:
            StanzaType: The type of the stanza
        """
        stanza_type = None

        if stanza_name.lower() == "default":
            stanza_type = StanzaType.DEFAULT
        elif stanza_name == "":  # Empty stanza []
            stanza_type = StanzaType.EMPTY_STANZA
        elif stanza_name == "*":  # Star stanza [*]
            stanza_type = StanzaType.STAR_STANZA
        elif "*::" in stanza_name:
            stanza_type = StanzaType.GLOBAL_WILDCARD
        elif re.search(
            r"::\*[^\]]+", stanza_name
        ):  # Wildcard followed by additional characters
            stanza_type = StanzaType.TYPE_WILDCARD_PREFIX
        elif "::*" in stanza_name:
            stanza_type = StanzaType.TYPE_WILDCARD
        elif "::" in stanza_name:
            stanza_type = StanzaType.TYPE_SPECIFIC
        else:
            stanza_type = StanzaType.APP_SPECIFIC  # App-specific stanzas like [perfmon]

        return stanza_type
