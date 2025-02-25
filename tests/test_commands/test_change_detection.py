"""Tests for the change detection functionality."""

import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

from bydefault.commands.change_detection import (
    _parse_conf_file,
    detect_file_changes,
    detect_stanza_changes,
    scan_directory,
)
from bydefault.models.change_detection import ChangeType


class TestChangeDetection(TestCase):
    """Test case for change detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.base_dir = Path(tempfile.mkdtemp())
        self.current_dir = Path(tempfile.mkdtemp())

        # Create some test files
        self.setup_test_files()

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directories
        shutil.rmtree(self.base_dir, ignore_errors=True)
        shutil.rmtree(self.current_dir, ignore_errors=True)

    def setup_test_files(self):
        """Set up test files in temporary directories."""
        # Create directory structure in base
        (self.base_dir / "default").mkdir()
        (self.base_dir / "local").mkdir()
        (self.base_dir / "metadata").mkdir()

        # Create directory structure in current
        (self.current_dir / "default").mkdir()
        (self.current_dir / "local").mkdir()
        (self.current_dir / "metadata").mkdir()

        # Create some conf files in base
        with open(self.base_dir / "default" / "app.conf", "w") as f:
            f.write("[install]\n")
            f.write("state = enabled\n")
            f.write("\n")
            f.write("[package]\n")
            f.write("id = test_app\n")
            f.write("check_for_updates = 1\n")

        with open(self.base_dir / "default" / "inputs.conf", "w") as f:
            f.write("[monitor://var/log]\n")
            f.write("index = main\n")
            f.write("sourcetype = syslog\n")
            f.write("\n")
            f.write("[monitor://var/log/messages]\n")
            f.write("index = system\n")
            f.write("sourcetype = syslog\n")

        # Create a binary-like file in base
        with open(self.base_dir / "default" / "binary.conf", "wb") as f:
            f.write(b"Some binary \x00 content")

        # Create some conf files in current with changes
        with open(self.current_dir / "default" / "app.conf", "w") as f:
            f.write("[install]\n")
            f.write("state = enabled\n")
            f.write("\n")
            f.write("[package]\n")
            f.write("id = test_app\n")
            f.write("check_for_updates = 0\n")  # Changed value
            f.write("version = 1.0.0\n")  # Added property

        with open(self.current_dir / "default" / "props.conf", "w") as f:
            f.write("[syslog]\n")
            f.write("TRANSFORMS-set = syslog-set\n")

        # Update binary file with different content
        with open(self.current_dir / "default" / "binary.conf", "wb") as f:
            f.write(b"Different binary \x00 content")

    def test_parse_conf_file(self):
        """Test parsing of .conf files."""
        # Test parsing app.conf
        app_conf_path = self.base_dir / "default" / "app.conf"
        stanzas = _parse_conf_file(app_conf_path)

        self.assertEqual(len(stanzas), 2)
        self.assertIn("install", stanzas)
        self.assertIn("package", stanzas)
        self.assertEqual(stanzas["install"]["state"], "enabled")
        self.assertEqual(stanzas["package"]["id"], "test_app")
        self.assertEqual(stanzas["package"]["check_for_updates"], "1")

    def test_detect_stanza_changes(self):
        """Test detection of changes between stanzas in files."""
        base_file = self.base_dir / "default" / "app.conf"
        current_file = self.current_dir / "default" / "app.conf"

        changes = detect_stanza_changes(base_file, current_file)

        # We should have one modified stanza: [package]
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].name, "package")
        self.assertEqual(changes[0].change_type, ChangeType.MODIFIED)

        # Check for specific setting changes
        self.assertIn("check_for_updates", changes[0].settings)
        self.assertEqual(changes[0].settings["check_for_updates"], ChangeType.MODIFIED)

        # Verify there's a setting change for version (added)
        version_changes = [
            sc for sc in changes[0].setting_changes if sc.name == "version"
        ]
        self.assertEqual(len(version_changes), 1)
        self.assertEqual(version_changes[0].change_type, ChangeType.ADDED)
        self.assertEqual(version_changes[0].local_value, "1.0.0")
        self.assertIsNone(version_changes[0].default_value)

        # Verify there's a setting change for check_for_updates (modified)
        check_updates_changes = [
            sc for sc in changes[0].setting_changes if sc.name == "check_for_updates"
        ]
        self.assertEqual(len(check_updates_changes), 1)
        self.assertEqual(check_updates_changes[0].change_type, ChangeType.MODIFIED)
        self.assertEqual(check_updates_changes[0].local_value, "0")
        self.assertEqual(check_updates_changes[0].default_value, "1")

    def test_detect_file_changes(self):
        """Test detection of changes between directories."""
        changes = detect_file_changes(self.base_dir, self.current_dir)

        # Sort changes by path for consistent testing
        changes.sort(key=lambda c: str(c.file_path))

        # We should have:
        # - app.conf (modified)
        # - binary.conf (modified)
        # - inputs.conf (removed)
        # - props.conf (added)
        self.assertEqual(len(changes), 4)

        # Check app.conf - should be modified with stanza changes
        self.assertEqual(str(changes[0].file_path), "default/app.conf")
        self.assertFalse(changes[0].is_new)
        self.assertEqual(len(changes[0].stanza_changes), 1)  # [package] is modified

        # Check binary.conf - should be modified without stanza changes (binary file)
        self.assertEqual(str(changes[1].file_path), "default/binary.conf")
        self.assertFalse(changes[1].is_new)
        self.assertEqual(
            len(changes[1].stanza_changes), 0
        )  # Binary files don't have stanza changes

        # Check inputs.conf - should be removed
        self.assertEqual(str(changes[2].file_path), "default/inputs.conf")
        self.assertFalse(changes[2].is_new)
        self.assertEqual(
            len(changes[2].stanza_changes), 0
        )  # Removed files don't have stanza changes

        # Check props.conf - should be added
        self.assertEqual(str(changes[3].file_path), "default/props.conf")
        self.assertTrue(changes[3].is_new)
        self.assertEqual(
            len(changes[3].stanza_changes), 0
        )  # Added files don't have stanza changes in our implementation

    def test_detect_file_changes_base_only(self):
        """Test detection of changes with only a base directory."""
        changes = detect_file_changes(self.base_dir)

        # Sort changes by path for consistent testing
        changes.sort(key=lambda c: str(c.file_path))

        # We should have all files in base marked as new
        self.assertEqual(len(changes), 3)

        for change in changes:
            self.assertTrue(change.is_new)

    def test_scan_directory(self):
        """Test scanning a directory for changes."""
        result = scan_directory(self.current_dir, self.base_dir)

        self.assertEqual(result.ta_path, self.current_dir)
        self.assertTrue(result.is_valid_ta)

        # Should have the same changes as test_detect_file_changes
        self.assertEqual(len(result.file_changes), 4)

    def test_scan_directory_no_baseline(self):
        """Test scanning a directory without a baseline."""
        result = scan_directory(self.base_dir)

        self.assertEqual(result.ta_path, self.base_dir)
        self.assertTrue(result.is_valid_ta)
        self.assertIsNone(result.error_message)

        # Should have the same changes as test_detect_file_changes_base_only
        self.assertEqual(len(result.file_changes), 3)

        for change in result.file_changes:
            self.assertTrue(change.is_new)

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with non-existent directory
        with self.assertRaises(ValueError):
            detect_file_changes(Path("/non/existent/path"))

        # Test with file instead of directory
        file_path = self.base_dir / "default" / "app.conf"
        with self.assertRaises(ValueError):
            detect_file_changes(file_path)

        # Test with invalid current directory
        with self.assertRaises(ValueError):
            detect_file_changes(self.base_dir, file_path)


class TestEdgeCases(TestCase):
    """Test edge cases for change detection."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.test_dir = Path(tempfile.mkdtemp())
        (self.test_dir / "base").mkdir()
        (self.test_dir / "current").mkdir()

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_empty_conf_file(self):
        """Test handling of empty conf files."""
        # Create empty conf files
        with open(self.test_dir / "base" / "empty.conf", "w") as f:
            pass

        with open(self.test_dir / "current" / "empty.conf", "w") as f:
            pass

        # Test stanza detection
        changes = detect_stanza_changes(
            self.test_dir / "base" / "empty.conf",
            self.test_dir / "current" / "empty.conf",
        )

        # Should be no changes
        self.assertEqual(len(changes), 0)

    def test_malformed_conf_file(self):
        """Test handling of malformed conf files."""
        # Create malformed conf files
        with open(self.test_dir / "base" / "malformed.conf", "w") as f:
            f.write("This is not a valid conf file\n")
            f.write("No stanza headers or key-value pairs\n")

        with open(self.test_dir / "current" / "malformed.conf", "w") as f:
            f.write("This is not a valid conf file\n")
            f.write("With different content\n")

        # Test stanza detection
        changes = detect_stanza_changes(
            self.test_dir / "base" / "malformed.conf",
            self.test_dir / "current" / "malformed.conf",
        )

        # Should be no changes since there are no valid stanzas
        self.assertEqual(len(changes), 0)

    def test_file_with_no_stanzas(self):
        """Test handling of files with key-value pairs but no stanzas."""
        # Create conf files with key-value pairs but no stanza headers
        with open(self.test_dir / "base" / "no_stanzas.conf", "w") as f:
            f.write("key1 = value1\n")
            f.write("key2 = value2\n")

        with open(self.test_dir / "current" / "no_stanzas.conf", "w") as f:
            f.write("key1 = value1\n")
            f.write("key2 = value3\n")  # Changed value

        # Test stanza detection
        changes = detect_stanza_changes(
            self.test_dir / "base" / "no_stanzas.conf",
            self.test_dir / "current" / "no_stanzas.conf",
        )

        # Should be no changes since there are no valid stanzas
        self.assertEqual(len(changes), 0)
