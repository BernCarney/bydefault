"""Parser for Splunk configuration files that preserves comments.

This module provides a parser for Splunk configuration files that
preserves comment relationships to stanzas and settings.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

    def parse(self) -> Tuple[Dict[str, Stanza], Dict[str, Setting]]:
        """Parse the configuration file.

        This method reads the configuration file and parses its content
        into a structured format that preserves comments and their
        associations with stanzas and settings.

        Returns:
            Tuple[Dict[str, Stanza], Dict[str, Setting]]: A tuple containing
                the stanzas and global settings

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
            UnicodeDecodeError: If the file encoding is not supported
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            # Parse the content
            for i, line in enumerate(content):
                line_number = i + 1

                # Check for blank lines
                if self.BLANK_LINE_PATTERN.match(line):
                    if self.current_stanza:
                        self.current_stanza.blank_lines_after += 1
                    continue

                # Check for comments
                comment_match = self.COMMENT_PATTERN.match(line)
                if comment_match:
                    self.pending_comments.append(
                        Comment(content=comment_match.group(1), line_number=line_number)
                    )
                    continue

                # Check for stanzas
                stanza_match = self.STANZA_PATTERN.match(line)
                if stanza_match:
                    stanza_name = stanza_match.group(1)
                    stanza_type = self._classify_stanza(stanza_name)

                    self.current_stanza = Stanza(
                        name=stanza_name, type=stanza_type, line_number=line_number
                    )

                    # Associate pending comments with this stanza
                    if self.pending_comments:
                        self.current_stanza.comments.extend(self.pending_comments)
                        self.pending_comments = []

                    self.stanzas[stanza_name] = self.current_stanza
                    continue

                # Check for settings
                setting_match = self.SETTING_PATTERN.match(line)
                if setting_match:
                    key = setting_match.group(1)
                    value = setting_match.group(2)

                    setting = Setting(key=key, value=value, line_number=line_number)

                    # Associate pending comments with this setting
                    if self.pending_comments:
                        setting.comments.extend(self.pending_comments)
                        self.pending_comments = []

                    if self.current_stanza:
                        self.current_stanza.settings[key] = setting
                    else:
                        self.global_settings[key] = setting

            # If there are any pending comments at the end, associate them with the last stanza
            if self.pending_comments and self.current_stanza:
                self.current_stanza.comments.extend(self.pending_comments)
                self.pending_comments = []

            return self.stanzas, self.global_settings

        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            raise e

    def _classify_stanza(self, stanza_name: str) -> StanzaType:
        """Classify a stanza based on its name.

        Args:
            stanza_name: The name of the stanza

        Returns:
            StanzaType: The type of the stanza
        """
        if stanza_name.lower() == "default":
            return StanzaType.DEFAULT
        elif "*::" in stanza_name:
            return StanzaType.GLOBAL_WILDCARD
        elif "::*" in stanza_name:
            return StanzaType.TYPE_WILDCARD
        elif "::*-" in stanza_name:
            return StanzaType.TYPE_WILDCARD_PREFIX
        elif "::" in stanza_name:
            return StanzaType.TYPE_SPECIFIC
        else:
            return StanzaType.GLOBAL
