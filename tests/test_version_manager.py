"""Tests for version management."""

from bydefault.core import version_manager


def test_read_ta_version(complete_ta_structure):
    """Test reading TA version."""
    version = version_manager.read_ta_version(complete_ta_structure)
    assert version == "1.0.0"


def test_update_ta_version(complete_ta_structure):
    """Test updating TA version."""
    success = version_manager.update_ta_version(complete_ta_structure, "2.0.0")
    assert success

    # Verify update
    version = version_manager.read_ta_version(complete_ta_structure)
    assert version == "2.0.0"


def test_find_tas(tmp_path, complete_ta_structure):
    """Test finding TAs in directory."""
    # Move complete TA to tmp_path and create additional test TAs
    complete_ta_structure.rename(tmp_path / complete_ta_structure.name)

    # Create additional test TAs
    ta2 = tmp_path / "TA-test2"
    not_ta = tmp_path / "NOT-TA"
    empty_ta = tmp_path / "TA-empty"

    # Set up TA-test2 with minimal structure
    (ta2 / "default").mkdir(parents=True)
    app_conf = ta2 / "default" / "app.conf"
    app_conf.write_text(
        """
[launcher]
version = 1.0.0

[package]
id = TA-test2
    """.strip()
    )

    # Set up non-TA directory
    not_ta.mkdir()
    (not_ta / "default").mkdir()
    (not_ta / "default" / "app.conf").touch()

    # Set up empty TA directory
    empty_ta.mkdir()

    tas = version_manager.find_tas(tmp_path)
    assert len(tas) == 2
    assert tmp_path / "TA-test" in tas
    assert ta2 in tas
    assert not_ta not in tas
    assert empty_ta not in tas


def test_read_ta_version_missing_file(tmp_path):
    """Test reading version from nonexistent app.conf."""
    version = version_manager.read_ta_version(tmp_path)
    assert version is None


def test_update_ta_version_missing_file(tmp_path):
    """Test updating version in nonexistent app.conf."""
    success = version_manager.update_ta_version(tmp_path, "2.0.0")
    assert not success


def test_update_ta_version_invalid_format(complete_ta_structure):
    """Test updating version with invalid format."""
    # Corrupt the app.conf file
    app_conf = complete_ta_structure / "default" / "app.conf"
    app_conf.write_text("Invalid content")

    success = version_manager.update_ta_version(complete_ta_structure, "2.0.0")
    assert not success
