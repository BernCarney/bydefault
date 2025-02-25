"""Tests for change detection models."""

from pathlib import Path

from bydefault.models.change_detection import (
    ChangeType,
    FileChange,
    ScanResult,
    SettingChange,
    StanzaChange,
)


class TestChangeType:
    """Tests for the ChangeType enum."""

    def test_enum_values(self):
        """Test that enum values are as expected."""
        assert ChangeType.ADDED.value == "added"
        assert ChangeType.MODIFIED.value == "modified"
        assert ChangeType.REMOVED.value == "removed"


class TestSettingChange:
    """Tests for the SettingChange class."""

    def test_init(self):
        """Test initialization with different parameters."""
        # Test with only required parameters
        setting = SettingChange(name="TEST", change_type=ChangeType.ADDED)
        assert setting.name == "TEST"
        assert setting.change_type == ChangeType.ADDED
        assert setting.local_value is None
        assert setting.default_value is None

        # Test with all parameters
        setting = SettingChange(
            name="TEST",
            change_type=ChangeType.MODIFIED,
            local_value="new_value",
            default_value="old_value",
        )
        assert setting.name == "TEST"
        assert setting.change_type == ChangeType.MODIFIED
        assert setting.local_value == "new_value"
        assert setting.default_value == "old_value"


class TestStanzaChange:
    """Tests for the StanzaChange class."""

    def test_init(self):
        """Test initialization with different parameters."""
        # Test with only required parameters
        stanza = StanzaChange(name="[stanza]", change_type=ChangeType.ADDED)
        assert stanza.name == "[stanza]"
        assert stanza.change_type == ChangeType.ADDED
        assert stanza.settings == {}
        assert stanza.setting_changes == []

        # Test with all parameters
        settings = {"key1": ChangeType.ADDED, "key2": ChangeType.MODIFIED}
        setting_changes = [
            SettingChange(name="key1", change_type=ChangeType.ADDED),
            SettingChange(name="key2", change_type=ChangeType.MODIFIED),
        ]
        stanza = StanzaChange(
            name="[stanza]",
            change_type=ChangeType.MODIFIED,
            settings=settings,
            setting_changes=setting_changes,
        )
        assert stanza.name == "[stanza]"
        assert stanza.change_type == ChangeType.MODIFIED
        assert stanza.settings == settings
        assert stanza.setting_changes == setting_changes

    def test_add_setting_change(self):
        """Test adding a setting change to a stanza."""
        stanza = StanzaChange(name="[stanza]", change_type=ChangeType.MODIFIED)

        # Add a simple setting change
        stanza.add_setting_change(name="key1", change_type=ChangeType.ADDED)
        assert len(stanza.settings) == 1
        assert len(stanza.setting_changes) == 1
        assert stanza.settings["key1"] == ChangeType.ADDED
        assert stanza.setting_changes[0].name == "key1"
        assert stanza.setting_changes[0].change_type == ChangeType.ADDED

        # Add a setting change with values
        stanza.add_setting_change(
            name="key2",
            change_type=ChangeType.MODIFIED,
            local_value="new",
            default_value="old",
        )
        assert len(stanza.settings) == 2
        assert len(stanza.setting_changes) == 2
        assert stanza.settings["key2"] == ChangeType.MODIFIED
        assert stanza.setting_changes[1].name == "key2"
        assert stanza.setting_changes[1].local_value == "new"
        assert stanza.setting_changes[1].default_value == "old"


class TestFileChange:
    """Tests for the FileChange class."""

    def test_init(self):
        """Test initialization with different parameters."""
        # Test with only required parameters
        file_change = FileChange(file_path=Path("local/props.conf"))
        assert file_change.file_path == Path("local/props.conf")
        assert file_change.stanza_changes == []
        assert file_change.is_new is False

        # Test with all parameters
        stanza_changes = [
            StanzaChange(name="[stanza1]", change_type=ChangeType.ADDED),
            StanzaChange(name="[stanza2]", change_type=ChangeType.MODIFIED),
        ]
        file_change = FileChange(
            file_path=Path("local/props.conf"),
            stanza_changes=stanza_changes,
            is_new=True,
        )
        assert file_change.file_path == Path("local/props.conf")
        assert file_change.stanza_changes == stanza_changes
        assert file_change.is_new is True

    def test_has_changes_property(self):
        """Test the has_changes property."""
        # File with no changes
        file_change = FileChange(file_path=Path("local/props.conf"))
        assert file_change.has_changes is False

        # File with changes
        file_change.stanza_changes.append(
            StanzaChange(name="[stanza]", change_type=ChangeType.ADDED)
        )
        assert file_change.has_changes is True


class TestScanResult:
    """Tests for the ScanResult class."""

    def test_init(self):
        """Test initialization with different parameters."""
        # Test with only required parameters
        scan_result = ScanResult(ta_path=Path("my_ta"))
        assert scan_result.ta_path == Path("my_ta")
        assert scan_result.file_changes == []
        assert scan_result.is_valid_ta is True
        assert scan_result.error_message is None

        # Test with all parameters
        file_changes = [
            FileChange(
                file_path=Path("local/props.conf"),
                stanza_changes=[
                    StanzaChange(name="[stanza]", change_type=ChangeType.ADDED)
                ],
            )
        ]
        scan_result = ScanResult(
            ta_path=Path("my_ta"),
            file_changes=file_changes,
            is_valid_ta=False,
            error_message="Invalid TA structure",
        )
        assert scan_result.ta_path == Path("my_ta")
        assert scan_result.file_changes == file_changes
        assert scan_result.is_valid_ta is False
        assert scan_result.error_message == "Invalid TA structure"

    def test_has_changes_property(self):
        """Test the has_changes property."""
        # No file changes
        scan_result = ScanResult(ta_path=Path("my_ta"))
        assert scan_result.has_changes is False

        # Empty file changes
        scan_result.file_changes.append(FileChange(file_path=Path("local/props.conf")))
        assert scan_result.has_changes is False

        # File with changes
        file_change = FileChange(file_path=Path("local/transforms.conf"))
        file_change.stanza_changes.append(
            StanzaChange(name="[stanza]", change_type=ChangeType.ADDED)
        )
        scan_result.file_changes.append(file_change)
        assert scan_result.has_changes is True
