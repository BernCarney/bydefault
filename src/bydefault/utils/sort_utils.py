"""Sort utilities for Splunk configuration files.

This module provides utilities for sorting Splunk configuration files
according to Splunk's logical priority order while preserving structure
and comments.
"""

from pathlib import Path
from typing import Dict

from bydefault.models.sort_models import StanzaType
from bydefault.utils.parser import CommentAwareParser
from bydefault.utils.writer import SortedConfigWriter


class ConfigSorter:
    """Main class for sorting Splunk configuration files.

    This class handles the parsing, sorting, and writing of Splunk
    configuration files while preserving structure and comments.

    Attributes:
        file_path: The path to the configuration file
        verbose: Whether to show detailed output
    """

    def __init__(self, file_path: Path, verbose: bool = False):
        """Initialize the ConfigSorter.

        Args:
            file_path: The path to the configuration file
            verbose: Whether to show detailed output
        """
        self.file_path = file_path
        self.verbose = verbose
        self.content = []
        self.stanzas = {}
        self.global_settings = {}
        self.parser = CommentAwareParser(self.file_path)

    def parse(self) -> None:
        """Parse the configuration file.

        This method reads the configuration file and parses its content
        into a structured format that preserves comments and their
        associations with stanzas and settings.

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
            UnicodeDecodeError: If the file encoding is not supported
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.content = f.readlines()

            # Use the CommentAwareParser to parse the file
            self.stanzas, self.global_settings = self.parser.parse()

        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            raise e

    def sort(self) -> Dict:
        """Sort the configuration file content.

        This method sorts the stanzas according to Splunk's logical
        priority order and sorts settings alphabetically within each
        stanza.

        Returns:
            Dict: A dictionary containing the sorting results
        """
        # Initialize the result dictionary
        result = {
            "stanzas_reordered": 0,
            "settings_sorted": 0,
            "comments_preserved": 0,
            "global_settings_count": len(self.global_settings),
            "default_stanza_found": False,
            "default_stanza_position": 0,
            "wildcard_stanzas": {},
            "specific_stanzas_groups": [],
            "warnings": [],
        }

        # Sort global settings alphabetically
        sorted_global_settings = {}
        for key in sorted(self.global_settings.keys()):
            sorted_global_settings[key] = self.global_settings[key]
            result["settings_sorted"] += 1

        self.global_settings = sorted_global_settings
        result["global_settings_count"] = len(self.global_settings)

        # Count the number of comments in global settings
        for setting in self.global_settings.values():
            result["comments_preserved"] += len(setting.comments)

        # Collect and categorize stanzas for sorting
        default_stanza = None
        empty_stanza = None
        star_stanza = None
        global_wildcard_stanzas = {}
        type_wildcard_stanzas = {}
        type_wildcard_prefix_stanzas = {}
        type_specific_stanzas = {}
        app_specific_stanzas = {}

        # Group stanzas by type
        for name, stanza in self.stanzas.items():
            if stanza.type == StanzaType.DEFAULT:
                default_stanza = stanza
                result["default_stanza_found"] = True
            elif stanza.type == StanzaType.EMPTY_STANZA:
                empty_stanza = stanza
            elif stanza.type == StanzaType.STAR_STANZA:
                star_stanza = stanza
            elif stanza.type == StanzaType.GLOBAL_WILDCARD:
                global_wildcard_stanzas[name] = stanza
            elif stanza.type == StanzaType.TYPE_WILDCARD:
                type_wildcard_stanzas[name] = stanza
            elif stanza.type == StanzaType.TYPE_WILDCARD_PREFIX:
                type_wildcard_prefix_stanzas[name] = stanza
            elif stanza.type == StanzaType.TYPE_SPECIFIC:
                type_specific_stanzas[name] = stanza
            elif stanza.type == StanzaType.APP_SPECIFIC:
                app_specific_stanzas[name] = stanza

        # Check for multiple global stanza types and issue warning if needed
        global_stanza_types = []
        if len(self.global_settings) > 0:  # Global settings outside stanzas
            global_stanza_types.append("*")
        if empty_stanza is not None:
            global_stanza_types.append("[]")
        if star_stanza is not None:
            global_stanza_types.append("[*]")
        if default_stanza is not None:
            global_stanza_types.append("[default]")

        if len(global_stanza_types) > 1:
            warning_msg = (
                f"Multiple global stanza types detected: "
                f"{', '.join(global_stanza_types)}. "
                "This may cause unexpected behavior in Splunk."
            )
            result["warnings"].append(warning_msg)

        # Sort settings within each stanza
        for stanza in self.stanzas.values():
            sorted_settings = {}
            for key in sorted(stanza.settings.keys()):
                sorted_settings[key] = stanza.settings[key]
                result["settings_sorted"] += 1
            stanza.settings = sorted_settings

            # Count comments in this stanza
            result["comments_preserved"] += len(stanza.comments)
            for setting in stanza.settings.values():
                result["comments_preserved"] += len(setting.comments)

        # Create a new ordered stanzas dictionary
        ordered_stanzas = {}

        # Order: * (settings outside stanzas) -> [] -> [*] -> [default]
        # handled by the SortedConfigWriter

        # 1. Empty stanza []
        if empty_stanza:
            ordered_stanzas[empty_stanza.name] = empty_stanza
            result["stanzas_reordered"] += 1

        # 2. Star stanza [*]
        if star_stanza:
            ordered_stanzas[star_stanza.name] = star_stanza
            result["stanzas_reordered"] += 1

        # 3. Default stanza
        if default_stanza:
            ordered_stanzas[default_stanza.name] = default_stanza
            result["default_stanza_position"] = len(ordered_stanzas) - 1

        # 4. App-specific stanzas (like [perfmon], [sourcetype], etc.)
        if app_specific_stanzas:
            for name in sorted(app_specific_stanzas.keys()):
                ordered_stanzas[name] = app_specific_stanzas[name]
                result["stanzas_reordered"] += 1

        # 5. Global wildcard stanzas
        if global_wildcard_stanzas:
            for name in sorted(global_wildcard_stanzas.keys()):
                ordered_stanzas[name] = global_wildcard_stanzas[name]
                result["wildcard_stanzas"][name] = len(ordered_stanzas) - 1
                result["stanzas_reordered"] += 1

        # Group specific stanzas by type (everything before ::)
        type_groups = {}
        for name, _stanza in type_specific_stanzas.items():
            stanza_type = name.split("::")[0] if "::" in name else ""
            if stanza_type not in type_groups:
                type_groups[stanza_type] = []
            type_groups[stanza_type].append(name)

        # Sort the type groups
        sorted_type_groups = sorted(type_groups.keys())
        result["specific_stanzas_groups"] = sorted_type_groups

        # 6. For each type group, add:
        #    a. Type wildcard stanzas
        #    b. Type wildcard prefix stanzas
        #    c. Type specific stanzas
        for stanza_type in sorted_type_groups:
            # a. Type wildcard stanzas for this type
            type_wildcard_key = f"{stanza_type}::*"
            if type_wildcard_key in type_wildcard_stanzas:
                ordered_stanzas[type_wildcard_key] = type_wildcard_stanzas[
                    type_wildcard_key
                ]
                result["stanzas_reordered"] += 1

            # b. Type wildcard prefix stanzas for this type (sorted by prefix)
            prefix_keys = [
                k
                for k in type_wildcard_prefix_stanzas.keys()
                if k.startswith(f"{stanza_type}::*-")
            ]
            for key in sorted(prefix_keys):
                ordered_stanzas[key] = type_wildcard_prefix_stanzas[key]
                result["stanzas_reordered"] += 1

            # c. Type specific stanzas for this type (sorted alphabetically)
            for name in sorted(type_groups[stanza_type]):
                ordered_stanzas[name] = type_specific_stanzas[name]
                result["stanzas_reordered"] += 1

        # Replace the stanzas dict with the ordered one
        self.stanzas = ordered_stanzas

        return result

    def write(self) -> None:
        """Write the sorted content back to the file.

        This method writes the sorted content back to the file,
        preserving the original file encoding and line endings.

        Raises:
            PermissionError: If the file cannot be written
        """
        try:
            # Use the SortedConfigWriter to write the sorted content
            writer = SortedConfigWriter(
                self.file_path, self.stanzas, self.global_settings
            )
            writer.write()
        except PermissionError as e:
            raise e
