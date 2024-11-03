"""Tests for Splunk operations."""

from bydefault.core.splunk_ops import SplunkConfManager


def test_get_local_configs(complete_ta_structure):
    """Test getting local configuration files."""
    manager = SplunkConfManager(complete_ta_structure)
    local_configs = manager.get_local_configs()

    # Check that we get all expected config files
    expected_configs = {
        "props.conf",
        "transforms.conf",
        "inputs.conf",
        "fields.conf",
        "eventtypes.conf",
        "tags.conf",
        "macros.conf",
        "web.conf",
    }
    found_configs = {p.name for p in local_configs}
    assert found_configs == expected_configs


def test_merge_conf_files(complete_ta_structure):
    """Test merging configuration files."""
    manager = SplunkConfManager(complete_ta_structure)
    local_props = complete_ta_structure / "local" / "props.conf"

    success, message = manager.merge_conf_files(local_props)
    assert success
    assert "Successfully merged" in message

    # Verify merged content
    merged_config = manager.read_conf_file(
        complete_ta_structure / "default" / "props.conf"
    )
    assert merged_config.has_section("test_sourcetype")
    assert merged_config.get("test_sourcetype", "TRANSFORMS-test") == "test_transform"
    assert merged_config.get("test_sourcetype", "SHOULD_LINEMERGE") == "false"
    assert merged_config.get("test_sourcetype", "TIME_PREFIX") == "timestamp="


def test_merge_meta(complete_ta_structure):
    """Test merging metadata files."""
    manager = SplunkConfManager(complete_ta_structure)

    success, message = manager.merge_meta()
    assert success
    assert "Successfully merged metadata" in message

    # Verify merged content
    merged_meta = manager.read_conf_file(
        complete_ta_structure / "metadata" / "default.meta"
    )
    assert merged_meta.has_section("props/test_sourcetype")
    assert (
        merged_meta.get("props/test_sourcetype", "access")
        == "read : [ * ], write : [ admin ]"
    )
    assert merged_meta.get("props/test_sourcetype", "owner") == "admin"


def test_merge_transforms(complete_ta_structure):
    """Test merging transforms.conf specifically."""
    manager = SplunkConfManager(complete_ta_structure)
    local_transforms = complete_ta_structure / "local" / "transforms.conf"

    success, message = manager.merge_conf_files(local_transforms)
    assert success
    assert "Successfully merged" in message

    # Verify merged content
    merged_config = manager.read_conf_file(
        complete_ta_structure / "default" / "transforms.conf"
    )
    # Test both transform and lookup sections
    assert merged_config.has_section("test_transform")
    assert merged_config.has_section("test_lookup")

    # Test transform section
    assert (
        merged_config.get("test_transform", "REGEX") == "timestamp=(\\d{10}\\.\\d{3})"
    )
    assert merged_config.get("test_transform", "FORMAT") == "timestamp::$1"
    assert merged_config.get("test_transform", "DEST_KEY") == "_time"

    # Test lookup section
    assert merged_config.get("test_lookup", "filename") == "test_lookup.csv"


def test_merge_nonexistent_file(complete_ta_structure):
    """Test attempting to merge a nonexistent file."""
    manager = SplunkConfManager(complete_ta_structure)
    nonexistent = complete_ta_structure / "local" / "nonexistent.conf"

    success, message = manager.merge_conf_files(nonexistent)
    assert not success
    assert "does not exist" in message


def test_merge_invalid_file(complete_ta_structure):
    """Test merging an invalid configuration file."""
    manager = SplunkConfManager(complete_ta_structure)
    invalid_conf = complete_ta_structure / "local" / "invalid.conf"

    # Create an invalid conf file
    invalid_conf.write_text("This is not a valid conf file")

    success, message = manager.merge_conf_files(invalid_conf)
    assert not success
    assert "Failed to merge" in message
