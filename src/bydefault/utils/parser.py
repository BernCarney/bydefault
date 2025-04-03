"""Parser for Splunk configuration files that preserves comments.

This module provides a parser for Splunk configuration files that
preserves comment relationships to stanzas and settings.
"""

import re
from pathlib import Path

from bydefault.models.sort_models import Setting, Stanza, StanzaType


class CommentAwareParser:
    """Parser that preserves comment relationships to stanzas and settings.

    This class parses Splunk configuration files and preserves comment
    relationships to stanzas and settings.

    Attributes:
        file_path: The path to the configuration file
        verbose: Whether to show detailed output
    """

    # Regular expressions for parsing
    STANZA_PATTERN = re.compile(r"^\s*\[(.*?)\]\s*$")
    SETTING_PATTERN = re.compile(r"^\s*([^=\s]+)\s*=\s*(.*?)(?:\s*#.*)?$")
    COMMENT_PATTERN = re.compile(r"^\s*#\s*(.*)\s*$")
    BLANK_LINE_PATTERN = re.compile(r"^\s*$")

    def __init__(self, file_path: Path, verbose: bool = False):
        """Initialize the parser.

        Args:
            file_path: The path to the configuration file
            verbose: Whether to show detailed output
        """
        self.file_path = file_path
        self.verbose = verbose
        self.content = []
        self.stanzas = {}
        self.global_settings = {}
        self.comments = []
        self.blank_lines = []
        self.current_stanza = None
        self.current_setting = None
        self.current_comment = None
        self.current_blank_lines = 0
        self.line_number = 0
        self.stanza_types = {}

    def parse(self):
        """Parse the configuration file.

        This method reads the configuration file and parses its content
        into a structured format that preserves comments and their
        associations with stanzas and settings.

        Returns:
            tuple: (stanzas, global_settings) where stanzas is a dict of
                stanza names to Stanza objects and global_settings is a
                dict of setting names to Setting objects
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    self.line_number += 1
                    line = line.rstrip("\n")

                    # Skip empty lines
                    if not line:
                        self.current_blank_lines += 1
                        continue

                    # Reset blank line counter
                    if self.current_blank_lines > 0:
                        self.blank_lines.append(self.current_blank_lines)
                        self.current_blank_lines = 0

                    # Check for stanza
                    stanza_match = self.STANZA_PATTERN.match(line)
                    if stanza_match:
                        stanza_name = stanza_match.group(1)
                        stanza_type = self._classify_stanza(stanza_name)
                        self.stanza_types[stanza_name] = stanza_type

                        # Create new stanza
                        self.current_stanza = Stanza(
                            name=stanza_name,
                            type=stanza_type,
                            line_number=self.line_number,
                            comments=self.comments.copy(),
                            blank_lines_after=self.blank_lines.copy(),
                        )
                        self.stanzas[stanza_name] = self.current_stanza
                        self.comments = []
                        self.blank_lines = []
                        continue

                    # Check for setting
                    setting_match = self.SETTING_PATTERN.match(line)
                    if setting_match:
                        key = setting_match.group(1)
                        value = setting_match.group(2)

                        # Create setting
                        setting = Setting(
                            key=key,
                            value=value,
                            line_number=self.line_number,
                            comments=self.comments.copy(),
                        )

                        # Add to current stanza or global settings
                        if self.current_stanza:
                            self.current_stanza.settings[key] = setting
                        else:
                            self.global_settings[key] = setting

                        self.comments = []
                        continue

                    # Check for comment
                    comment_match = self.COMMENT_PATTERN.match(line)
                    if comment_match:
                        comment = comment_match.group(1)
                        self.comments.append(comment)
                        continue

            # For debugging - only show in verbose mode
            if self.verbose:
                print("Stanza Types:")
                for name, typ in self.stanza_types.items():
                    print(f"  {name}: {typ}")

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
