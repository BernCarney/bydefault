"""Utility functions for merge command functionality.

This module provides the core functionality for merging configuration files
between local and default directories while preserving structure and comments.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

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

            # Handle metadata files (local.meta -> default.meta)
            metadata_dir = self.ta_dir / "metadata"
            local_meta = metadata_dir / "local.meta"
            default_meta = metadata_dir / "default.meta"

            if local_meta.exists():
                try:
                    file_result = self._merge_file(local_meta, default_meta)
                    self.result.add_file_result(file_result)
                    self._merged_files[local_meta] = file_result
                except Exception as e:
                    # If metadata file fails, create a result with error
                    file_result = FileMergeResult(file_path=local_meta, error=str(e))
                    self.result.add_file_result(file_result)
                    self._merged_files[local_meta] = file_result

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

            # Handle metadata files (they're in metadata directory
            # instead of local/default)
            if local_file.name == "local.meta" and "metadata" in str(local_file):
                default_file = self.ta_dir / "metadata" / "default.meta"
            else:
                default_file = self.default_dir / local_file.name

            try:
                # If default file doesn't exist yet, simply copy the local file
                if not default_file.exists():
                    self._copy_file(local_file, default_file)
                    continue

                # Create file content from scratch
                local_sorter = ConfigSorter(local_file, verbose=self.verbose)
                default_sorter = ConfigSorter(default_file, verbose=self.verbose)

                local_sorter.parse()
                default_sorter.parse()

                # For replace mode, completely replace stanzas from local
                if self.mode == MergeMode.REPLACE:
                    for stanza_name, local_stanza in local_sorter.stanzas.items():
                        if stanza_name in default_sorter.stanzas:
                            # Replace all settings in the stanza
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
                    for stanza_name, local_stanza in local_sorter.stanzas.items():
                        if stanza_name not in default_sorter.stanzas:
                            # Add new stanza
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
                            default_stanza = default_sorter.stanzas[stanza_name]

                            # Update or add settings from local
                            for setting_key, setting in local_stanza.settings.items():
                                default_stanza.settings[setting_key] = Setting(
                                    key=setting.key,
                                    value=setting.value,
                                    line_number=setting.line_number,
                                    comments=setting.comments.copy(),
                                )

                # Write files safely with fallback
                try:
                    # Write changes to a temporary string first to validate
                    with open(default_file, "w", encoding="utf-8") as f:
                        # Manual formatting to avoid writer errors
                        for stanza_name, stanza in default_sorter.stanzas.items():
                            # Write stanza header
                            f.write(f"[{stanza_name}]\n")

                            # Write stanza settings
                            for setting_key, setting in stanza.settings.items():
                                if setting.value is not None:
                                    f.write(f"{setting_key} = {setting.value}\n")
                                else:
                                    f.write(f"{setting_key}\n")

                            # Add blank line between stanzas
                            f.write("\n")
                except Exception:
                    # Fallback: Copy the local file to default if
                    # we can't write properly
                    self._copy_file(local_file, default_file)

            except Exception as e:
                file_result.error = f"Error writing file: {str(e)}"

    def _merge_file(
        self, local_file: Path, target_file: Optional[Path] = None
    ) -> FileMergeResult:
        """Merge a single configuration file.

        Args:
            local_file: Path to the local configuration file
            target_file: Optional target file path (for metadata files)

        Returns:
            FileMergeResult: Results of merging the file
        """
        result = FileMergeResult(file_path=local_file)

        try:
            # Get corresponding default file (either specified or inferred)
            if target_file:
                default_file = target_file
            else:
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
                    stanza_result = StanzaMergeResult(
                        name=stanza_name, type=stanza.type, is_new=True
                    )
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
            for stanza_name, default_stanza in default_sorter.stanzas.items():
                if stanza_name not in local_sorter.stanzas:
                    result.preserved_stanzas.add(stanza_name)
                    # Create a stanza result for preserved stanzas
                    stanza_result = StanzaMergeResult(
                        name=stanza_name, type=default_stanza.type
                    )
                    stanza_result.settings_preserved.update(
                        default_stanza.settings.keys()
                    )
                    result.stanza_results[stanza_name] = stanza_result

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
        result = StanzaMergeResult(name=name, type=local_stanza.type)

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

    def cleanup_local_files(self) -> List[Path]:
        """Remove local files that were successfully merged and clean up empty local
        directory.

        After a successful merge operation, this removes the files from the local
        directory that were merged into default. If the local directory becomes empty,
        it will be removed as well. Also handles local.meta files in the
        metadata directory.

        Returns:
            List[Path]: List of paths to removed files
        """
        removed_files = []

        # Only remove files that were successfully merged
        for file_path, file_result in self._merged_files.items():
            if file_result.success:
                try:
                    # Check if file still exists (it might have been removed already)
                    if file_path.exists():
                        os.remove(file_path)
                        removed_files.append(file_path)
                except Exception as e:
                    # If removal fails, continue with other files
                    print(f"Warning: Failed to remove {file_path}: {str(e)}")

        # Check if local directory is empty and remove it if so
        if self.local_dir.exists():
            remaining_files = list(self.local_dir.iterdir())
            if not remaining_files:
                try:
                    os.rmdir(self.local_dir)
                    print(f"Removed empty local directory: {self.local_dir}")
                except Exception as e:
                    print(f"Warning: Failed to remove empty local directory: {str(e)}")

        return removed_files
