"""Tests for the merge utility functions."""

from pathlib import Path

import pytest

from bydefault.models.merge_models import FileMergeResult, MergeMode, MergeResult
from bydefault.utils.merge_utils import ConfigMerger


@pytest.fixture
def ta_dir(tmp_path):
    """Create a temporary TA directory structure for testing."""
    ta = tmp_path / "test_ta"
    ta.mkdir()

    local = ta / "local"
    default = ta / "default"
    local.mkdir()
    default.mkdir()

    # Create test files
    create_test_files(local, default)

    return ta


def create_test_files(local, default):
    """Create test configuration files."""
    # File present in both directories
    local_inputs = local / "inputs.conf"
    local_inputs.write_text(
        """
[monitor://test]
index = main
sourcetype = test_data
disabled = false
# Local comment

[monitor://new_input]
index = security
sourcetype = security_logs
disabled = false
"""
    )

    default_inputs = default / "inputs.conf"
    default_inputs.write_text(
        """
[monitor://test]
index = main
sourcetype = old_data
disabled = true
# Default comment

[monitor://existing]
index = internal
sourcetype = internal_logs
disabled = true
"""
    )

    # File only in local
    local_only = local / "local_only.conf"
    local_only.write_text(
        """
[stanza1]
key1 = value1
key2 = value2
"""
    )

    # File with multi-line values
    local_props = local / "props.conf"
    local_props.write_text(
        """
[sourcetype]
TRANSFORMS-app = app_transform
REPORT-fields = extract-fields
EVAL-new_field = case(
    field1="value1", "result1",
    field1="value2", "result2",
    1=1, "default"
)
"""
    )

    default_props = default / "props.conf"
    default_props.write_text(
        """
[sourcetype]
TRANSFORMS-app = old_transform
EVAL-old_field = "static"
"""
    )


def test_merger_initialization(ta_dir):
    """Test ConfigMerger initialization."""
    merger = ConfigMerger(ta_dir)

    assert merger.ta_dir == ta_dir
    assert merger.local_dir == ta_dir / "local"
    assert merger.default_dir == ta_dir / "default"
    assert merger.mode == MergeMode.MERGE
    assert not merger.verbose


def test_merger_merge_new_file(ta_dir):
    """Test merging a file that exists only in local."""
    merger = ConfigMerger(ta_dir)
    result = merger.merge()

    assert result.success
    assert len(result.file_results) > 0

    # Find the local_only.conf result
    local_only_result = None
    for file_result in result.file_results:
        if file_result.file_path.name == "local_only.conf":
            local_only_result = file_result
            break

    assert local_only_result is not None
    assert local_only_result.success
    assert "*" in local_only_result.new_stanzas  # All stanzas are new


def test_merger_merge_existing_file(ta_dir):
    """Test merging a file that exists in both directories."""
    merger = ConfigMerger(ta_dir)
    result = merger.merge()

    assert result.success

    # Find the inputs.conf result
    inputs_result = None
    for file_result in result.file_results:
        if file_result.file_path.name == "inputs.conf":
            inputs_result = file_result
            break

    assert inputs_result is not None
    assert inputs_result.success

    # Check expected stanzas
    assert "monitor://new_input" in inputs_result.new_stanzas  # New stanza
    assert "monitor://test" in inputs_result.merged_stanzas  # Updated stanza
    assert "monitor://existing" in inputs_result.preserved_stanzas  # Unchanged stanza

    # Check individual stanza results
    test_stanza = inputs_result.stanza_results["monitor://test"]
    assert not test_stanza.is_new
    assert "sourcetype" in test_stanza.settings_updated  # Updated setting
    assert "disabled" in test_stanza.settings_updated  # Updated setting

    new_stanza = inputs_result.stanza_results["monitor://new_input"]
    assert new_stanza.is_new
    assert "index" in new_stanza.settings_added
    assert "sourcetype" in new_stanza.settings_added
    assert "disabled" in new_stanza.settings_added


def test_merger_merge_with_multiline_values(ta_dir):
    """Test merging a file with multi-line values."""
    merger = ConfigMerger(ta_dir)
    result = merger.merge()

    assert result.success

    # Find the props.conf result
    props_result = None
    for file_result in result.file_results:
        if file_result.file_path.name == "props.conf":
            props_result = file_result
            break

    assert props_result is not None
    assert props_result.success

    # Check that multi-line value was processed correctly
    sourcetype_stanza = props_result.stanza_results["sourcetype"]
    assert "TRANSFORMS-app" in sourcetype_stanza.settings_updated
    assert "EVAL-new_field" in sourcetype_stanza.settings_added
    assert "EVAL-old_field" in sourcetype_stanza.settings_preserved


def test_merger_replace_mode(ta_dir):
    """Test merger in replace mode."""
    merger = ConfigMerger(ta_dir, mode=MergeMode.REPLACE)
    result = merger.merge()

    assert result.success

    # Find the inputs.conf result
    inputs_result = None
    for file_result in result.file_results:
        if file_result.file_path.name == "inputs.conf":
            inputs_result = file_result
            break

    assert inputs_result is not None
    assert inputs_result.success

    # In replace mode, all settings should be updated
    test_stanza = inputs_result.stanza_results["monitor://test"]
    assert "index" in test_stanza.settings_updated
    assert "sourcetype" in test_stanza.settings_updated
    assert "disabled" in test_stanza.settings_updated


def test_merger_write(ta_dir):
    """Test writing merged changes to files."""
    merger = ConfigMerger(ta_dir)
    merger.merge()
    merger.write()

    # Verify merged file contents
    default_inputs = ta_dir / "default" / "inputs.conf"
    content = default_inputs.read_text()

    # Should contain content from both files
    assert "monitor://test" in content
    assert "monitor://new_input" in content
    assert "monitor://existing" in content
    assert "sourcetype = test_data" in content  # Updated from local
    assert "disabled = false" in content  # Updated from local

    # Check if new file was created
    assert (ta_dir / "default" / "local_only.conf").exists()

    # Check if multi-line values were preserved
    props_content = (ta_dir / "default" / "props.conf").read_text()
    assert "EVAL-new_field = case(" in props_content
    assert 'field1 = "value2", "result2",' in props_content
    assert 'EVAL-old_field = "static"' in props_content  # Preserved from default


def test_merger_error_handling(ta_dir):
    """Test error handling in merger."""
    # Create a file with an error
    error_file = FileMergeResult(file_path=Path("invalid.conf"), error="Test error")

    # Create a merge result with the error file
    result = MergeResult()
    result.add_file_result(error_file)

    # Overall merge should fail if any file has an error
    assert not result.success

    # The file should be marked as failed
    assert not error_file.success
    assert error_file.error == "Test error"


def test_merge_multiline_values(tmp_path):
    """Test that the merge command correctly handles multiline values."""
    # Create a simple TA directory structure
    ta_dir = tmp_path / "test_ta"
    local_dir = ta_dir / "local"
    default_dir = ta_dir / "default"
    local_dir.mkdir(parents=True)
    default_dir.mkdir(parents=True)

    # Create a local file with a multiline value
    local_file = local_dir / "test.conf"
    local_content = """[test]
multiline_value = line1 \\
line2 \\
line3
single_value = simple value
"""
    local_file.write_text(local_content)

    # Create a default file with a single-line value
    default_file = default_dir / "test.conf"
    default_content = """[test]
existing_value = default value
"""
    default_file.write_text(default_content)

    # Print initial files for debugging
    print(f"\nLOCAL CONTENT:\n{local_file.read_text()}")
    print(f"\nDEFAULT CONTENT (BEFORE):\n{default_file.read_text()}")

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify that the merge was successful
    assert result.success

    # Read the merged file
    merged_content = default_file.read_text()
    print(f"\nMERGED CONTENT:\n{merged_content}")

    # Verify that multiline values are preserved correctly
    assert "multiline_value = line1 \\" in merged_content
    assert "line2 \\" in merged_content
    assert "line3" in merged_content
    assert "single_value = simple value" in merged_content
    assert "existing_value = default value" in merged_content

    # Make sure the lines are in the correct order
    lines = merged_content.splitlines()
    multiline_start_index = lines.index(
        [l for l in lines if "multiline_value = line1" in l][0]
    )
    assert "line2" in lines[multiline_start_index + 1]
    assert "line3" in lines[multiline_start_index + 2]


def test_merge_multiline_values_realistic(tmp_path):
    """Test merging with realistic multiline values."""
    # Create a simple TA directory structure
    ta_dir = tmp_path / "test_ta"
    local_dir = ta_dir / "local"
    default_dir = ta_dir / "default"
    local_dir.mkdir(parents=True)
    default_dir.mkdir(parents=True)

    # Create a local file with a multiline value - no indentation
    local_file = local_dir / "test.conf"
    local_content = """[test]
multiline_value = line1 \\
line2 \\
line3
single_value = simple value
"""
    local_file.write_text(local_content)

    # Create a default file with a single-line value
    default_file = default_dir / "test.conf"
    default_content = """[test]
existing_value = default value
"""
    default_file.write_text(default_content)

    print(f"\nLOCAL CONTENT:\n{local_file.read_text()}")
    print(f"\nDEFAULT CONTENT (BEFORE):\n{default_file.read_text()}")

    # IMPORTANT: Use the same parsing approach as change_detection
    # to get the correct parsing of multi-line values
    from bydefault.utils.change_detection import _parse_conf_file

    # Parse the local content with the proven method
    parsed_local = _parse_conf_file(local_file)
    print(f"\nParsed local multiline_value: {parsed_local['test']['multiline_value']}")

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Read merged file
    merged_content = default_file.read_text()
    print(f"\nMERGED CONTENT:\n{merged_content}")

    # Parse the merged content
    parsed_merged = _parse_conf_file(default_file)
    print(
        f"\nParsed merged multiline_value: {parsed_merged['test'].get('multiline_value', 'NOT FOUND')}"
    )

    # Check if the multiline value structure was preserved
    assert "multiline_value = line1 \\" in merged_content
    assert "line2 \\" in merged_content
    assert "line3" in merged_content

    # Check if the parsed value is correct
    assert "multiline_value" in parsed_merged["test"]
    assert (
        parsed_merged["test"]["multiline_value"]
        == parsed_local["test"]["multiline_value"]
    )
