"""Utility functions for merge command functionality.

This module provides the core functionality for merging configuration files
between local and default directories while preserving structure and comments.
"""

import shutil
from pathlib import Path
from typing import Dict, Optional

from bydefault.models.merge_models import (
    FileMergeResult,
    MergeMode,
    MergeResult,
    StanzaMergeResult,
)
from bydefault.models.sort_models import Setting, Stanza
from bydefault.utils.sort_utils import ConfigSorter


class ConfigMerger:
    """Handles merging of configuration files between local and default directories."""

    def __init__(
        self,
        ta_dir: Path,
        mode: MergeMode = MergeMode.MERGE,
        verbose: bool = False,
    ) -> None:
        """Initialize the merger.

        Args:
            ta_dir: Path to the TA directory
            mode: How to handle local changes
            verbose: Whether to show detailed output
        """
        self.ta_dir = ta_dir
        self.mode = mode
        self.verbose = verbose
        self.local_dir = ta_dir / "local"
        self.default_dir = ta_dir / "default"
        self.result = MergeResult()
        self._merged_files: Dict[Path, FileMergeResult] = {}

    def merge(self) -> MergeResult:
        """Merge configuration files from local to default.

        Returns:
            MergeResult: Results of the merge operation
        """
        try:
            # Find all configuration files in local
            local_files = list(self.local_dir.glob("*.conf"))

            # Process each file
            for local_file in local_files:
                try:
                    file_result = self._merge_file(local_file)
                    self.result.add_file_result(file_result)
                    self._merged_files[local_file] = file_result
                except Exception as e:
                    # If a file fails, create a result with error
                    file_result = FileMergeResult(file_path=local_file, error=str(e))
                    self.result.add_file_result(file_result)
                    self._merged_files[local_file] = file_result

            return self.result

        except Exception as e:
            self.result.error = str(e)
            return self.result

    def write(self) -> None:
        """Write merged configurations to default directory."""
        for file_result in self.result.file_results:
            if not file_result.success:
                continue

            # Get the local file path
            local_file = file_result.file_path
            default_file = self.default_dir / local_file.name

            try:
                # If default file doesn't exist yet, simply copy the local file
                if not default_file.exists():
                    print(
                        f"DEBUG: Default file {default_file} doesn't exist, copying from local"
                    )
                    self._copy_file(local_file, default_file)
                    continue

                # Create file content from scratch
                local_sorter = ConfigSorter(local_file, verbose=self.verbose)
                default_sorter = ConfigSorter(default_file, verbose=self.verbose)

                local_sorter.parse()
                default_sorter.parse()

                print(f"DEBUG: Local stanzas: {list(local_sorter.stanzas.keys())}")
                print(
                    f"DEBUG: Default stanzas before merge: {list(default_sorter.stanzas.keys())}"
                )

                # For replace mode, completely replace stanzas from local
                if self.mode == MergeMode.REPLACE:
                    print("DEBUG: Using REPLACE mode")
                    for stanza_name, local_stanza in local_sorter.stanzas.items():
                        if stanza_name in default_sorter.stanzas:
                            # Replace all settings in the stanza
                            print(f"DEBUG: Replacing stanza {stanza_name}")
                            default_stanza = default_sorter.stanzas[stanza_name]
                            default_stanza.settings = {}  # Clear existing settings

                            # Copy settings from local to default
                            for setting_key, setting in local_stanza.settings.items():
                                default_stanza.settings[setting_key] = Setting(
                                    key=setting.key,
                                    value=setting.value,
                                    line_number=setting.line_number,
                                    comments=setting.comments.copy(),
                                )
                        else:
                            # Add new stanza
                            print(f"DEBUG: Adding new stanza {stanza_name}")
                            # Create a new stanza with the same type
                            new_stanza = Stanza(
                                name=stanza_name,
                                type=local_stanza.type,
                                line_number=local_stanza.line_number,
                                comments=local_stanza.comments.copy(),
                                blank_lines_after=local_stanza.blank_lines_after,
                            )

                            # Copy settings
                            for setting_key, setting in local_stanza.settings.items():
                                new_stanza.settings[setting_key] = Setting(
                                    key=setting.key,
                                    value=setting.value,
                                    line_number=setting.line_number,
                                    comments=setting.comments.copy(),
                                )

                            default_sorter.stanzas[stanza_name] = new_stanza
                else:  # Merge mode
                    print("DEBUG: Using MERGE mode")
                    for stanza_name, local_stanza in local_sorter.stanzas.items():
                        if stanza_name not in default_sorter.stanzas:
                            # Add new stanza
                            print(f"DEBUG: Adding new stanza {stanza_name}")
                            # Create a new stanza with the same type
                            new_stanza = Stanza(
                                name=stanza_name,
                                type=local_stanza.type,
                                line_number=local_stanza.line_number,
                                comments=local_stanza.comments.copy(),
                                blank_lines_after=local_stanza.blank_lines_after,
                            )

                            # Copy settings
                            for setting_key, setting in local_stanza.settings.items():
                                new_stanza.settings[setting_key] = Setting(
                                    key=setting.key,
                                    value=setting.value,
                                    line_number=setting.line_number,
                                    comments=setting.comments.copy(),
                                )

                            default_sorter.stanzas[stanza_name] = new_stanza
                        else:
                            # Update values in existing stanza
                            print(f"DEBUG: Updating stanza {stanza_name}")
                            default_stanza = default_sorter.stanzas[stanza_name]

                            # Update or add settings from local
                            for setting_key, setting in local_stanza.settings.items():
                                default_stanza.settings[setting_key] = Setting(
                                    key=setting.key,
                                    value=setting.value,
                                    line_number=setting.line_number,
                                    comments=setting.comments.copy(),
                                )

                print(
                    f"DEBUG: Default stanzas after merge: {list(default_sorter.stanzas.keys())}"
                )

                # Write changes to file
                default_sorter.write()

                # Verify the file was written correctly
                print(f"DEBUG: Default file after write: {default_file.read_text()}")

            except Exception as e:
                print(f"DEBUG: Error during write: {str(e)}")
                file_result.error = f"Error writing file: {str(e)}"

    def _merge_file(self, local_file: Path) -> FileMergeResult:
        """Merge a single configuration file.

        Args:
            local_file: Path to the local configuration file

        Returns:
            FileMergeResult: Results of merging the file
        """
        result = FileMergeResult(file_path=local_file)

        try:
            # Get corresponding default file
            default_file = self.default_dir / local_file.name

            # Parse the local file
            local_sorter = ConfigSorter(local_file, verbose=self.verbose)
            try:
                local_sorter.parse()
            except Exception as parse_e:
                # Handle parsing errors specifically
                result.error = f"Error parsing file: {str(parse_e)}"
                return result

            # If default file doesn't exist, all stanzas are new
            if not default_file.exists():
                result.new_stanzas.add("*")  # Mark all stanzas as new
                for stanza_name, stanza in local_sorter.stanzas.items():
                    stanza_result = StanzaMergeResult(name=stanza_name, is_new=True)
                    stanza_result.settings_added.update(stanza.settings.keys())
                    result.stanza_results[stanza_name] = stanza_result
                return result

            # Parse default file
            default_sorter = ConfigSorter(default_file, verbose=self.verbose)
            try:
                default_sorter.parse()
            except Exception as parse_e:
                # Handle parsing errors specifically
                result.error = f"Error parsing default file: {str(parse_e)}"
                return result

            # Process each stanza in local
            for stanza_name, local_stanza in local_sorter.stanzas.items():
                stanza_result = self._merge_stanza(
                    stanza_name,
                    local_stanza,
                    default_sorter.stanzas.get(stanza_name),
                )
                result.stanza_results[stanza_name] = stanza_result

                if stanza_result.is_new:
                    result.new_stanzas.add(stanza_name)
                else:
                    result.merged_stanzas.add(stanza_name)

            # Track preserved stanzas (only in default)
            for stanza_name in default_sorter.stanzas:
                if stanza_name not in local_sorter.stanzas:
                    result.preserved_stanzas.add(stanza_name)

            return result

        except Exception as e:
            result.error = str(e)
            return result

    def _merge_stanza(
        self,
        name: str,
        local_stanza: Stanza,
        default_stanza: Optional[Stanza],
    ) -> StanzaMergeResult:
        """Merge a single stanza.

        Args:
            name: Name of the stanza
            local_stanza: Settings from local stanza
            default_stanza: Settings from default stanza (if exists)

        Returns:
            StanzaMergeResult: Results of merging the stanza
        """
        result = StanzaMergeResult(name=name)

        try:
            if default_stanza is None:
                # New stanza
                result.is_new = True
                result.settings_added.update(local_stanza.settings.keys())
                return result

            if self.mode == MergeMode.REPLACE:
                # Replace mode: use only local settings
                result.settings_updated.update(local_stanza.settings.keys())
                return result

            # Merge mode: combine settings
            for key, setting in local_stanza.settings.items():
                if key not in default_stanza.settings:
                    result.settings_added.add(key)
                elif default_stanza.settings[key].value != setting.value:
                    result.settings_updated.add(key)

            # Track preserved settings
            for key in default_stanza.settings:
                if key not in local_stanza.settings:
                    result.settings_preserved.add(key)

            return result

        except Exception as e:
            result.error = str(e)
            return result

    def _copy_file(self, src: Path, dst: Path) -> None:
        """Copy a file while preserving metadata.

        Args:
            src: Source file path
            dst: Destination file path
        """
        shutil.copy2(src, dst)
