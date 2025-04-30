"""Utility functions for merge command functionality.

This module provides the core functionality for merging configuration files
between local and default directories while preserving structure and comments.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from bydefault.models.merge_models import (
    FileMergeResult,
    MergeMode,
    MergeResult,
    StanzaMergeResult,
)
from bydefault.models.sort_models import Stanza
from bydefault.utils.change_detection import _parse_conf_file
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
        """Write merged configurations to default directory.

        This method handles writing merged configurations back to the file system.
        It preserves stanza order and comments from the original files.
        """
        for file_result in self.result.file_results:
            if not file_result.success:
                continue

            # Get the local file path
            local_file = file_result.file_path

            # Handle metadata files (they're in metadata directory instead of local/default)
            if local_file.name == "local.meta" and "metadata" in str(local_file):
                default_file = self.ta_dir / "metadata" / "default.meta"
            else:
                default_file = self.default_dir / local_file.name

            try:
                # If default file doesn't exist yet, simply copy the local file
                if not default_file.exists():
                    self._copy_file(local_file, default_file)
                    continue

                # Parse both files to get complete stanza information
                local_parsed = _parse_conf_file(local_file)
                default_parsed = _parse_conf_file(default_file)

                # Read the full local file content for multiline detection
                with open(local_file, "r", encoding="utf-8") as f:
                    local_content = f.read()

                # Create a backup of the default file
                default_backup = None
                try:
                    import shutil

                    default_backup = default_file.with_suffix(
                        default_file.suffix + ".bak"
                    )
                    shutil.copy(default_file, default_backup)
                except Exception:
                    # If backup fails, continue without backup
                    pass

                # Prepare merged configuration
                merged_config = self._prepare_merged_config(
                    local_parsed, default_parsed
                )

                try:
                    # Write merged configuration to file
                    self._write_merged_file(default_file, merged_config, local_content)

                    # Delete backup if all went well
                    if default_backup and default_backup.exists():
                        default_backup.unlink()
                except Exception as e:
                    # Restore backup if available
                    if default_backup and default_backup.exists():
                        try:
                            shutil.copy(default_backup, default_file)
                            default_backup.unlink()
                        except Exception:
                            pass
                    # Re-raise the exception
                    raise e

            except Exception as e:
                # Log the error
                file_result.error = f"Error writing file: {str(e)}"
                if self.verbose:
                    print(f"Error writing file {default_file}: {str(e)}")
                    import traceback

                    traceback.print_exc()

    def _prepare_merged_config(self, local_parsed, default_parsed):
        """Prepare the merged configuration based on local and default settings.

        Args:
            local_parsed: Dictionary of stanzas from local file
            default_parsed: Dictionary of stanzas from default file

        Returns:
            Dictionary containing the merged configuration
        """
        merged_config = {}

        # Start with all settings from default
        for stanza_name, settings in default_parsed.items():
            merged_config[stanza_name] = settings.copy()

        # Add or update settings from local based on merge mode
        for stanza_name, settings in local_parsed.items():
            # If stanza doesn't exist in merged_config, add it
            if stanza_name not in merged_config:
                merged_config[stanza_name] = {}

            # Replace or merge settings based on mode
            if self.mode == MergeMode.REPLACE:
                # Replace entire stanza with local version
                merged_config[stanza_name] = settings.copy()
            else:
                # Update settings from local
                for setting_key, setting_value in settings.items():
                    merged_config[stanza_name][setting_key] = setting_value

        return merged_config

    def _write_merged_file(self, output_file, merged_config, local_content):
        """Write the merged configuration to a file.

        Args:
            output_file: Path to the output file
            merged_config: Dictionary containing the merged configuration
            local_content: String containing the local file content for multiline detection
        """

        # List of settings to avoid duplicates
        written_settings = {}

        with open(output_file, "w", encoding="utf-8") as f:
            # Process each stanza
            for stanza_name, settings in merged_config.items():
                # Write stanza header
                f.write(f"[{stanza_name}]\n")
                written_settings[stanza_name] = set()

                # First directly process multiline values from the local file
                multiline_settings = set()

                # Directly find multiline settings in the local file
                stanza_pattern = rf"\[{re.escape(stanza_name)}\](.*?)(?=\n\[|\Z)"
                stanza_matches = re.search(stanza_pattern, local_content, re.DOTALL)

                if stanza_matches:
                    stanza_content = stanza_matches.group(1)
                    # Find individual settings with continuation characters
                    lines = stanza_content.split("\n")
                    i = 0

                    while i < len(lines):
                        line = lines[i].strip()

                        # Check if this is a setting line
                        if "=" in line and not line.startswith("#"):
                            setting_key, setting_value = line.split("=", 1)
                            setting_key = setting_key.strip()

                            # Only process settings that are in our merged config
                            if setting_key in settings:
                                # Check if this is potentially a multiline setting
                                if "\\" in setting_value:
                                    # This is a multiline setting
                                    multiline_lines = [line]

                                    # Collect all continuation lines
                                    j = i + 1
                                    current_line = line

                                    while j < len(lines) and (
                                        "\\" in current_line or j == i + 1
                                    ):
                                        current_line = lines[j].strip()
                                        if not current_line.startswith(
                                            "["
                                        ):  # Not a new stanza
                                            multiline_lines.append(current_line)
                                            j += 1
                                        else:
                                            break

                                    if len(multiline_lines) > 1:
                                        # Write multiline setting
                                        multiline_settings.add(setting_key)

                                        # Write setting line
                                        f.write(
                                            f"{setting_key} = {setting_value.strip()}\n"
                                        )

                                        # Write continuation lines
                                        for ml_line in multiline_lines[1:]:
                                            f.write(f"{ml_line}\n")

                                        written_settings.setdefault(
                                            stanza_name, set()
                                        ).add(setting_key)
                                        i = (
                                            j - 1
                                        )  # Update index to skip processed lines

                        i += 1

                # Process regular settings
                for setting_key, setting_value in sorted(settings.items()):
                    if setting_key not in written_settings.get(stanza_name, set()):
                        f.write(f"{setting_key} = {setting_value}\n")
                        written_settings.setdefault(stanza_name, set()).add(setting_key)

                # Add blank lines after each stanza
                f.write("\n\n")

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
