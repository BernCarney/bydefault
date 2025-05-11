"""Writer for sorted Splunk configuration files.

This module provides a writer for sorted Splunk configuration files
that preserves structure and comments.
"""

from pathlib import Path
from typing import Dict, List

from bydefault.models.sort_models import Setting, Stanza, StanzaType


class SortedConfigWriter:
    """Writer for sorted Splunk configuration files.

    This class writes sorted Splunk configuration files while
    preserving structure and comments.

    Note:
        Future refactoring: The file writing functionality in this class should be
        extracted to a common utility function shared with ConfigMerger.write()
        to ensure consistent behavior between the merge and sort commands.

    Attributes:
        file_path: The path to the configuration file
        stanzas: The stanzas to write
        global_settings: The global settings to write
    """

    def __init__(
        self,
        file_path: Path,
        stanzas: Dict[str, Stanza],
        global_settings: Dict[str, Setting],
    ):
        """Initialize the writer.

        Args:
            file_path: The path to the configuration file
            stanzas: The stanzas to write
            global_settings: The global settings to write
        """
        self.file_path = file_path
        self.stanzas = stanzas
        self.global_settings = global_settings
        self.output_lines: List[str] = []

    def write(self) -> None:
        """Write the sorted content to the file.

        Raises:
            PermissionError: If the file cannot be written
        """
        self._generate_output()

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(self.output_lines)
        except PermissionError as e:
            raise e

    def _generate_output(self) -> None:
        """Generate the output lines.

        This method generates the output lines for the sorted
        configuration file.
        """
        # Clear the output lines
        self.output_lines = []

        # Write global settings first (outside of any stanza)
        if self.global_settings:
            self._write_global_settings()
            self.output_lines.append("\n")

        # Write stanzas in order of priority: [] -> [*] -> [default] -> ...
        self._write_empty_stanza()
        self._write_star_stanza()
        self._write_default_stanza()
        self._write_app_specific_stanzas()
        self._write_global_wildcard_stanzas()
        self._write_type_specific_stanzas()

    def _write_empty_stanza(self) -> None:
        """Write the empty stanza [].

        This method writes the empty stanza to the output lines if it exists.
        """
        # Find the empty stanza
        empty_stanza = None
        for stanza in self.stanzas.values():
            if stanza.type == StanzaType.EMPTY_STANZA:
                empty_stanza = stanza
                break

        # Write the empty stanza if it exists
        if empty_stanza:
            self._write_stanza(empty_stanza)

    def _write_star_stanza(self) -> None:
        """Write the star stanza [*].

        This method writes the star stanza to the output lines if it exists.
        """
        # Find the star stanza
        star_stanza = None
        for stanza in self.stanzas.values():
            if stanza.type == StanzaType.STAR_STANZA:
                star_stanza = stanza
                break

        # Write the star stanza if it exists
        if star_stanza:
            self._write_stanza(star_stanza)

    def _write_global_settings(self) -> None:
        """Write the global settings.

        This method writes the global settings to the output lines.
        """
        # Sort the global settings by key
        sorted_settings = sorted(self.global_settings.items())

        for _key, setting in sorted_settings:
            # Write comments associated with this setting
            for comment in setting.comments:
                # Handle both Comment objects and string comments
                if hasattr(comment, "content"):
                    self.output_lines.append(f"# {comment.content}\n")
                else:
                    self.output_lines.append(f"# {comment}\n")

            # Write the setting
            self._write_setting(setting, self)

    def _write_default_stanza(self) -> None:
        """Write the default stanza.

        This method writes the default stanza to the output lines.
        """
        # Find the default stanza
        default_stanza = None
        for stanza in self.stanzas.values():
            if stanza.type == StanzaType.DEFAULT:
                default_stanza = stanza
                break

        # Write the default stanza if it exists
        if default_stanza:
            self._write_stanza(default_stanza)

    def _write_app_specific_stanzas(self) -> None:
        """Write the app-specific stanzas.

        This method writes app-specific stanzas (like [perfmon]) to the output lines.
        """
        # Find all app-specific stanzas
        app_specific_stanzas = []
        for stanza in self.stanzas.values():
            if stanza.type == StanzaType.APP_SPECIFIC:
                app_specific_stanzas.append(stanza)

        # Sort app-specific stanzas by name
        app_specific_stanzas.sort(key=lambda s: s.name)

        # Write each app-specific stanza
        for stanza in app_specific_stanzas:
            self._write_stanza(stanza)

    def _write_global_wildcard_stanzas(self) -> None:
        """Write the global wildcard stanzas.

        This method writes the global wildcard stanzas to the output lines.
        """
        # Find the global wildcard stanzas
        global_wildcard_stanzas = []
        for stanza in self.stanzas.values():
            if stanza.type == StanzaType.GLOBAL_WILDCARD:
                global_wildcard_stanzas.append(stanza)

        # Sort by name
        global_wildcard_stanzas.sort(key=lambda s: s.name)

        # Write the stanzas
        for stanza in global_wildcard_stanzas:
            self._write_stanza(stanza)

    def _write_type_specific_stanzas(self) -> None:
        """Write the type-specific stanzas.

        This method writes the type-specific stanzas to the output lines.
        """
        # Group stanzas by type
        type_groups = {}
        for stanza in self.stanzas.values():
            if stanza.type in (
                StanzaType.TYPE_WILDCARD,
                StanzaType.TYPE_WILDCARD_PREFIX,
                StanzaType.TYPE_SPECIFIC,
            ):
                # Extract the type from the stanza name
                parts = stanza.name.split("::", 1)
                if len(parts) == 2:
                    type_name = parts[0]
                    if type_name not in type_groups:
                        type_groups[type_name] = []
                    type_groups[type_name].append(stanza)

        # Sort the groups by type name
        sorted_types = sorted(type_groups.keys())

        # Write the stanzas for each type
        for type_name in sorted_types:
            stanzas = type_groups[type_name]

            # Sort by priority and name
            stanzas.sort(
                key=lambda s: (
                    # Priority order: TYPE_WILDCARD, TYPE_WILDCARD_PREFIX, TYPE_SPECIFIC
                    0
                    if s.type == StanzaType.TYPE_WILDCARD
                    else 1
                    if s.type == StanzaType.TYPE_WILDCARD_PREFIX
                    else 2,
                    # Then by name
                    s.name,
                )
            )

            # Write the stanzas
            for stanza in stanzas:
                self._write_stanza(stanza)

    def _write_stanza(self, stanza: Stanza) -> None:
        """Write a stanza.

        Args:
            stanza: The stanza to write
        """
        # Write comments associated with this stanza
        for comment in stanza.comments:
            # Handle both Comment objects and string comments
            if hasattr(comment, "content"):
                self.output_lines.append(f"# {comment.content}\n")
            else:
                self.output_lines.append(f"# {comment}\n")

        # Write the stanza header
        self.output_lines.append(f"[{stanza.name}]\n")

        # Sort the settings by key
        sorted_settings = sorted(stanza.settings.items())

        # Write the settings
        for _key, setting in sorted_settings:
            # Write comments associated with this setting
            for comment in setting.comments:
                # Handle both Comment objects and string comments
                if hasattr(comment, "content"):
                    self.output_lines.append(f"# {comment.content}\n")
                else:
                    self.output_lines.append(f"# {comment}\n")

            # Write the setting
            self._write_setting(setting, self)

        # Add blank lines after the stanza - handle both int and list
        blank_lines = 1  # Default
        if isinstance(stanza.blank_lines_after, int):
            blank_lines = stanza.blank_lines_after
        elif isinstance(stanza.blank_lines_after, list) and stanza.blank_lines_after:
            # If it's a list, take the first value if available
            try:
                blank_lines = int(stanza.blank_lines_after[0])
            except (ValueError, TypeError):
                # Fallback to default if conversion fails
                blank_lines = 1

        for _ in range(blank_lines):
            self.output_lines.append("\n")

    def _write_setting(self, setting: Setting, _) -> None:
        """Write a setting.

        Args:
            setting: The setting to write
            _: Unused parameter (for backward compatibility)
        """
        # Write the setting
        if setting.key and setting.value is not None:
            # Check if this is a multi-line value (ends with backslash)
            is_multiline = False

            if isinstance(setting.value, str):
                # Check for backslash at the end or within the value
                if setting.value.strip().endswith("\\") or " \\" in setting.value:
                    is_multiline = True

            if is_multiline and hasattr(setting, "raw_content") and setting.raw_content:
                # Use the original raw content to preserve exact formatting
                # Ensure it ends with a newline
                content = setting.raw_content
                if not content.endswith("\n"):
                    content += "\n"
                self.output_lines.append(content)
            else:
                # Regular single-line setting
                self.output_lines.append(f"{setting.key} = {setting.value}\n")
        elif setting.key:
            # Handle settings with no value
            self.output_lines.append(f"{setting.key}\n")
