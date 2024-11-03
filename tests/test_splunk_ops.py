"""Tests for Splunk operations."""

import pytest
from pathlib import Path
from bydefault.core.splunk_ops import SplunkConfManager


@pytest.fixture
def temp_ta_structure(tmp_path):
    """Create a temporary TA structure for testing."""
    ta_root = tmp_path / "TA-test"
    local_dir = ta_root / "local"
    default_dir = ta_root / "default"
    meta_dir = ta_root / "metadata"

    # Create directories
    local_dir.mkdir(parents=True)
    default_dir.mkdir(parents=True)
    meta_dir.mkdir(parents=True)

    # Create test files
    local_props = local_dir / "props.conf"
    local_props.write_text(
        """
[test_sourcetype]
TRANSFORMS-test = test_transform
SHOULD_LINEMERGE = false
    """.strip()
    )

    default_props = default_dir / "props.conf"
    default_props.write_text(
        """
[test_sourcetype]
SHOULD_LINEMERGE = true
MAX_EVENTS = 1000
    """.strip()
    )

    local_meta = meta_dir / "local.meta"
    local_meta.write_text(
        """
[props/test_sourcetype]
owner = admin
version = 8.0.0
    """.strip()
    )

    return ta_root


def test_get_local_configs(temp_ta_structure):
    """Test getting local configuration files."""
    manager = SplunkConfManager(temp_ta_structure)
    local_configs = manager.get_local_configs()

    assert len(local_configs) == 1
    assert (temp_ta_structure / "local" / "props.conf") in local_configs


def test_merge_conf_files(temp_ta_structure):
    """Test merging configuration files."""
    manager = SplunkConfManager(temp_ta_structure)
    local_props = temp_ta_structure / "local" / "props.conf"

    success, message = manager.merge_conf_files(local_props)
    assert success
    assert "Successfully merged" in message

    # Verify merged content
    merged_config = manager.read_conf_file(temp_ta_structure / "default" / "props.conf")
    assert merged_config.has_section("test_sourcetype")
    assert merged_config.get("test_sourcetype", "TRANSFORMS-test") == "test_transform"
    assert merged_config.get("test_sourcetype", "SHOULD_LINEMERGE") == "false"
    assert merged_config.get("test_sourcetype", "MAX_EVENTS") == "1000"


def test_merge_meta(temp_ta_structure):
    """Test merging metadata files."""
    manager = SplunkConfManager(temp_ta_structure)

    success, message = manager.merge_meta()
    assert success
    assert "Successfully merged metadata" in message

    # Verify merged content
    merged_meta = manager.read_conf_file(
        temp_ta_structure / "metadata" / "default.meta"
    )
    assert merged_meta.has_section("props/test_sourcetype")
    assert merged_meta.get("props/test_sourcetype", "owner") == "admin"
    assert merged_meta.get("props/test_sourcetype", "version") == "8.0.0"
