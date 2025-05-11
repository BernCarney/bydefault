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
            # Read the entire file content
            with open(self.file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Convert any Windows line endings to Unix
            file_content = file_content.replace("\r\n", "\n")

            # Split into lines with line endings preserved
            lines = file_content.splitlines(keepends=True)
            i = 0

            # Process each line
            while i < len(lines):
                line = lines[i].rstrip("\n")
                self.line_number = i + 1

                # Skip empty lines but count them
                if not line.strip():
                    self.current_blank_lines += 1
                    i += 1
                    continue

                # Reset blank line counter if we have accumulated any
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
                    i += 1
                    continue

                # Check for setting
                setting_match = self.SETTING_PATTERN.match(line)
                if setting_match:
                    setting_key = setting_match.group(1).strip()
                    setting_value = setting_match.group(2).strip()
                    start_line_idx = i

                    # Detect if this is a multiline setting
                    multiline = setting_value.endswith("\\")

                    # Store the raw content with exact formatting
                    raw_content = lines[i]

                    # If multiline, collect all continuation lines
                    if multiline:
                        inside_multiline = True
                        j = i + 1

                        while j < len(lines) and inside_multiline:
                            next_line = lines[j]
                            next_line_stripped = next_line.strip()

                            # Empty lines or comments within a multiline value
                            if not next_line_stripped or next_line_stripped.startswith(
                                "#"
                            ):
                                raw_content += next_line
                                j += 1
                                continue

                            # Check if we've hit a new stanza
                            if self.STANZA_PATTERN.match(next_line_stripped):
                                inside_multiline = False
                                break

                            # Check for a new setting (begins with a word followed by =)
                            # But exclude lines that are indented, which are continuations
                            if self.SETTING_PATTERN.match(
                                next_line_stripped
                            ) and not next_line.startswith((" ", "\t")):
                                inside_multiline = False
                                break

                            # Add to raw content
                            raw_content += next_line

                            # If the line doesn't end with backslash, check next line
                            if not next_line_stripped.endswith("\\"):
                                # Look ahead to see if next non-empty, non-comment line
                                # is a new setting/stanza or continues this multi-line
                                k = j + 1
                                found_next_content = False

                                while k < len(lines) and not found_next_content:
                                    peek_line = lines[k].strip()
                                    if not peek_line or peek_line.startswith("#"):
                                        # Skip empty lines and comments
                                        k += 1
                                        continue

                                    # Found next content line
                                    found_next_content = True

                                    # If it's a new stanza or setting, we're done
                                    if self.STANZA_PATTERN.match(peek_line) or (
                                        self.SETTING_PATTERN.match(peek_line)
                                        and not lines[k].startswith((" ", "\t"))
                                    ):
                                        inside_multiline = False

                                    break

                                if not inside_multiline:
                                    break

                            j += 1

                        # Update our position
                        i = j
                    else:
                        # Single line setting
                        i += 1

                    # Create the setting
                    setting = Setting(
                        key=setting_key,
                        value=setting_value,
                        line_number=start_line_idx + 1,  # 1-indexed
                        comments=self.comments.copy(),
                        raw_content=raw_content,
                    )

                    # Add to the appropriate location
                    if self.current_stanza:
                        self.current_stanza.settings[setting_key] = setting
                    else:
                        self.global_settings[setting_key] = setting

                    # Clear comments for next setting
                    self.comments = []
                    continue

                # Check for comment
                comment_match = self.COMMENT_PATTERN.match(line)
                if comment_match:
                    comment = comment_match.group(1)
                    self.comments.append(comment)
                    i += 1
                    continue

                # Unrecognized line
                i += 1

            # For debugging - only show in verbose mode
            if self.verbose:
                print("Stanza Types:")
                for name, typ in self.stanza_types.items():
                    print(f"  {name}: {typ}")

                print("\nMultiline Settings:")
                for stanza_name, stanza in self.stanzas.items():
                    for key, setting in stanza.settings.items():
                        if (
                            hasattr(setting, "raw_content")
                            and "\\" in setting.raw_content
                        ):
                            print(f"  [{stanza_name}] {key}")

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
