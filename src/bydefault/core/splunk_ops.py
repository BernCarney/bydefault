"""Operations for managing Splunk TA configurations."""

from pathlib import Path
from typing import List, Tuple, Dict, Set
import shutil
import configparser


class SplunkConfManager:
    """Manages Splunk configuration file operations."""

    CONF_TYPES = {
        "props.conf",
        "transforms.conf",
        "inputs.conf",
        "app.conf",
        "eventtypes.conf",
        "tags.conf",
        "fields.conf",
        "macros.conf",
    }

    def __init__(self, ta_path: Path):
        """
        Initialize the configuration manager.

        Args:
            ta_path: Path to the TA directory
        """
        self.ta_path = ta_path
        self.local_path = ta_path / "local"
        self.default_path = ta_path / "default"
        self.meta_path = ta_path / "metadata"

    def get_local_configs(self) -> Set[Path]:
        """Get all configuration files in local directory."""
        if not self.local_path.exists():
            return set()

        return {p for p in self.local_path.glob("*.conf") if p.name in self.CONF_TYPES}

    def read_conf_file(self, path: Path) -> configparser.ConfigParser:
        """
        Read a Splunk configuration file.

        Args:
            path: Path to configuration file

        Returns:
            ConfigParser object with the file contents
        """
        config = configparser.ConfigParser(
            allow_no_value=True, strict=False, interpolation=None
        )
        config.optionxform = str  # Preserve case in keys

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                config.read_file(f)

        return config

    def merge_conf_files(self, local_path: Path) -> Tuple[bool, str]:
        """
        Merge a local configuration file into its default counterpart.

        Args:
            local_path: Path to local configuration file

        Returns:
            Tuple of (success, message)
        """
        if not local_path.exists():
            return False, f"Local file {local_path} does not exist"

        default_path = self.default_path / local_path.name

        # Read configurations
        local_conf = self.read_conf_file(local_path)
        default_conf = self.read_conf_file(default_path)

        # Merge sections from local to default
        for section in local_conf.sections():
            if not default_conf.has_section(section):
                default_conf.add_section(section)

            for key, value in local_conf.items(section):
                default_conf.set(section, key, value)

        # Create default directory if it doesn't exist
        self.default_path.mkdir(exist_ok=True)

        # Write merged configuration
        try:
            with open(default_path, "w", encoding="utf-8") as f:
                default_conf.write(f)
            return True, f"Successfully merged {local_path.name}"
        except Exception as e:
            return False, f"Failed to merge {local_path.name}: {str(e)}"

    def merge_meta(self) -> Tuple[bool, str]:
        """
        Merge local.meta into default.meta.

        Returns:
            Tuple of (success, message)
        """
        local_meta = self.meta_path / "local.meta"
        default_meta = self.meta_path / "default.meta"

        if not local_meta.exists():
            return False, "local.meta does not exist"

        try:
            local_conf = self.read_conf_file(local_meta)
            default_conf = self.read_conf_file(default_meta)

            # Merge metadata
            for section in local_conf.sections():
                if not default_conf.has_section(section):
                    default_conf.add_section(section)

                for key, value in local_conf.items(section):
                    default_conf.set(section, key, value)

            # Ensure metadata directory exists
            self.meta_path.mkdir(exist_ok=True)

            # Write merged metadata
            with open(default_meta, "w", encoding="utf-8") as f:
                default_conf.write(f)

            return True, "Successfully merged metadata"
        except Exception as e:
            return False, f"Failed to merge metadata: {str(e)}"
