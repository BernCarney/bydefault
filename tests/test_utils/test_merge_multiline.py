"""Tests for the merge utility's handling of multi-line values."""

import shutil
from pathlib import Path

import pytest

from bydefault.models.merge_models import MergeMode
from bydefault.utils.change_detection import _parse_conf_file
from bydefault.utils.merge_utils import ConfigMerger


def setup_test_dirs(tmp_path, fixture_file):
    """Set up test directories with fixture file."""
    # Create a test TA directory structure
    ta_dir = tmp_path / "test_ta"
    local_dir = ta_dir / "local"
    default_dir = ta_dir / "default"
    local_dir.mkdir(parents=True)
    default_dir.mkdir(parents=True)

    # Get the path to the fixture file
    current_dir = Path(__file__).parent
    fixture_path = current_dir.parent / "fixtures" / "merge" / fixture_file

    if not fixture_path.exists():
        pytest.fail(f"Fixture file not found: {fixture_path}")

    # Copy the fixture to both directories with modifications for testing
    shutil.copy(fixture_path, local_dir / fixture_file)

    return ta_dir, local_dir, default_dir, fixture_path


def create_modified_version(source_path, target_path, modifications):
    """Create a modified version of the source file.

    Args:
        source_path: Path to the source file
        target_path: Path to write the modified file
        modifications: Dict of {pattern: replacement} to apply
    """
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    for pattern, replacement in modifications.items():
        content = content.replace(pattern, replacement)

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)


def compare_multiline_values(file1, file2, stanza, setting):
    """Compare multiline values between two files."""
    stanzas1 = _parse_conf_file(file1)
    stanzas2 = _parse_conf_file(file2)

    # Check if the stanza exists in both files
    assert stanza in stanzas1, f"Stanza {stanza} not found in {file1}"
    assert stanza in stanzas2, f"Stanza {stanza} not found in {file2}"

    # Check if the setting exists in both stanzas
    assert (
        setting in stanzas1[stanza]
    ), f"Setting {setting} not found in {stanza} in {file1}"
    assert (
        setting in stanzas2[stanza]
    ), f"Setting {setting} not found in {stanza} in {file2}"

    # Compare the values
    value1 = stanzas1[stanza][setting]
    value2 = stanzas2[stanza][setting]

    # Get the raw lines from both files for comparison
    with open(file1, "r", encoding="utf-8") as f:
        content1 = f.read()
    with open(file2, "r", encoding="utf-8") as f:
        content2 = f.read()

    return value1, value2, content1, content2


def test_merge_complex_multiline_with_comments():
    """Test merging files with complex multiline values and embedded comments."""
    # This is a fixture-based test that will be implemented when the fixture is available
    pass


def test_merge_complex_search_commands(tmp_path):
    """Test merging of complex search commands with multiline values."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "complex_multiline.conf"
    )

    # Create a simpler version for the default directory with some changes
    default_file = default_dir / "complex_multiline.conf"
    modifications = {
        "search = index=main sourcetype=access_combined": "search = index=main sourcetype=access_logs",
        "earliest=-24h": "earliest=-12h",
        "head 100": "head 50",
    }
    create_modified_version(fixture_path, default_file, modifications)

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Compare the search setting values
    local_value, merged_value, local_content, merged_content = compare_multiline_values(
        local_dir / "complex_multiline.conf",
        default_dir / "complex_multiline.conf",
        "search_commands",
        "search",
    )

    # The local version should have overwritten the default version
    assert "sourcetype=access_combined" in merged_value
    assert "earliest=-24h" in merged_value
    assert "head 100" in merged_value

    # The multiline structure should be preserved with line breaks
    search_lines = [
        line
        for line in merged_content.splitlines()
        if "search =" in line or "| " in line
    ]

    assert len(search_lines) >= 5  # Should have at least 5 lines for this search
    assert any("search = " in line and "\\" in line for line in search_lines)
    assert any("| fields" in line for line in search_lines)
    assert any("| stats count" in line for line in search_lines)
    assert any("| sort" in line for line in search_lines)
    assert any("| head" in line for line in search_lines)


def test_merge_nested_case_statements(tmp_path):
    """Test merging of nested case statements with multiple levels of indentation."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "complex_multiline.conf"
    )

    # Create a modified version for the default directory
    default_file = default_dir / "complex_multiline.conf"
    modifications = {
        'match(message, ".*OutOfMemory.*"), "critical"': 'match(message, ".*OutOfMemory.*"), "fatal"',
        'true(), "info"': 'true(), "normal"',
    }
    create_modified_version(fixture_path, default_file, modifications)

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Compare the EVAL-severity_level values
    local_value, merged_value, local_content, merged_content = compare_multiline_values(
        local_dir / "complex_multiline.conf",
        default_dir / "complex_multiline.conf",
        "transforms",
        "EVAL-severity_level",
    )

    # The local version should have overwritten the default version
    assert 'match(message, ".*OutOfMemory.*"), "critical"' in merged_content
    assert 'true(), "info"' in merged_content

    # The nested structure should be preserved
    eval_lines = [
        line.strip()
        for line in merged_content.splitlines()
        if "EVAL-severity_level" in line
        or "match(" in line
        or "case(" in line
        or ")," in line
    ]

    # Check that indentation levels are preserved
    indentation_levels = set()
    for line in merged_content.splitlines():
        if "match(" in line:
            # Count leading spaces to check indentation preservation
            indentation_levels.add(len(line) - len(line.lstrip()))

    # Should have at least 2 different indentation levels for nested statements
    assert len(indentation_levels) >= 2


def test_merge_embedded_comments_in_multiline(tmp_path):
    """Test merging of multiline values with embedded comments."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "complex_multiline.conf"
    )

    # Create a modified version for the default directory
    default_file = default_dir / "complex_multiline.conf"
    modifications = {
        "# This comment should be preserved in the exact position": "# This comment has been modified",
        "search_with_comments = index=security sourcetype=firewall": "search_with_comments = index=security sourcetype=waf",
    }
    create_modified_version(fixture_path, default_file, modifications)

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Read the merged file
    merged_content = (default_dir / "complex_multiline.conf").read_text()

    # The local version should overwrite the default
    assert "# This comment should be preserved in the exact position" in merged_content
    assert "search_with_comments = index=security sourcetype=firewall" in merged_content

    # Check that embedded comments in the multiline value are preserved
    assert "# This describes the following operation" in merged_content


def test_merge_json_payload(tmp_path):
    """Test merging of complex JSON payloads in multiline format."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "complex_multiline.conf"
    )

    # Create a modified version for the default directory
    default_file = default_dir / "complex_multiline.conf"
    modifications = {
        '"alert_name": "$name$"': '"alert_id": "$id$", "alert_name": "$name$"',
        '"description": "This alert was triggered': '"summary": "Alert summary", "description": "This alert was modified',
    }
    create_modified_version(fixture_path, default_file, modifications)

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Read the merged file
    merged_content = (default_dir / "complex_multiline.conf").read_text()

    # The local version should have overwritten the default
    assert '"alert_name": "$name$"' in merged_content
    assert '"description": "This alert was triggered' in merged_content
    assert '"alert_id"' not in merged_content
    assert '"summary": "Alert summary"' not in merged_content

    # The JSON structure should be preserved with proper indentation
    json_lines = [
        line
        for line in merged_content.splitlines()
        if "action.payload" in line or '"' in line
    ]

    # Check for proper indentation in the JSON structure
    indentation_counts = {}
    for line in json_lines:
        if '"' in line:
            indent = len(line) - len(line.lstrip())
            indentation_counts[indent] = indentation_counts.get(indent, 0) + 1

    # Should have multiple indentation levels for a properly formatted JSON
    assert len(indentation_counts) >= 3


def test_merge_multiple_multiline_values_replacement(tmp_path):
    """Test replacing multiple multiline values in the same file."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "complex_multiline.conf"
    )

    # Create a modified version for the default directory
    default_file = default_dir / "complex_multiline.conf"

    # Create a version with more significant changes
    with open(fixture_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Modify multiple stanzas and settings for a more comprehensive test
    modified_content = (
        content.replace("[search_commands]", "[search_commands_modified]")
        .replace("REGEX-extract_fields", "REGEX-extract_modified")
        .replace("[alert:complex_automation]", "[alert:simple_automation]")
    )

    with open(default_file, "w", encoding="utf-8") as f:
        f.write(modified_content)

    # Merge the files using REPLACE mode to test full stanza replacement
    merger = ConfigMerger(ta_dir, mode=MergeMode.REPLACE)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Read the merged file
    merged_content = (default_dir / "complex_multiline.conf").read_text()

    # The local version should completely replace the default
    assert "[search_commands]" in merged_content
    assert "[search_commands_modified]" not in merged_content
    assert "REGEX-extract_fields" in merged_content
    assert "REGEX-extract_modified" not in merged_content
    assert "[alert:complex_automation]" in merged_content
    assert "[alert:simple_automation]" not in merged_content


def test_merge_splunk_transforms_conf(tmp_path):
    """Test merging with realistic Splunk transforms.conf file containing complex multi-line values."""
    # Set up test directories
    ta_dir, local_dir, default_dir, fixture_path = setup_test_dirs(
        tmp_path, "splunk_transforms.conf"
    )

    # Create a modified version for the default directory with multiple changes
    default_file = default_dir / "splunk_transforms.conf"
    modifications = {
        # Change severity calculation logic
        'match(message, ".*(OutOfMemory|OOM).*"), "critical_system"': 'match(message, ".*(OutOfMemory|OOM|Memory Allocation Failed).*"), "critical_memory"',
        # Modify the complex search filter
        '"| where block_count > 5 "': '"| where block_count > 10 "',
        # Change custom log extraction regex
        "([A-F0-9]{8})          # 8-character hex ID": "([A-F0-9]{8,12})       # 8-12 character hex ID",
        # Modify validation logic
        "isnotnull(user) AND len(user) > 0": "isnotnull(user_id) AND len(user_id) > 0",
    }
    create_modified_version(fixture_path, default_file, modifications)

    # Merge the files
    merger = ConfigMerger(ta_dir)
    result = merger.merge()
    merger.write()

    # Verify the merge was successful
    assert result.success

    # Read the merged file
    merged_content = (default_dir / "splunk_transforms.conf").read_text()

    # Verify that the local versions of modified settings were preserved
    assert '.*(OutOfMemory|OOM).*"), "critical_system"' in merged_content
    assert "block_count > 5" in merged_content
    assert "([A-F0-9]{8})          # 8-character hex ID" in merged_content
    assert "isnotnull(user) AND len(user) > 0" in merged_content

    # Check that complex nested cases are preserved
    assert 'match(message, ".*timeout.*"), "network_error"' in merged_content

    # Check that comment structure in multi-line values is preserved
    assert "# Start of line with case-insensitive and verbose mode" in merged_content
    assert "# Whitespace" in merged_content

    # Check that continuations are preserved
    assert 'true(), "broken" \\' in merged_content

    # Verify formatting of nested structures by examining indentation in merged content
    indentation_levels = {}
    for line in merged_content.splitlines():
        if "case(" in line or "match(" in line:
            # Count leading spaces to check indentation preservation
            indent = len(line) - len(line.lstrip())
            if indent in indentation_levels:
                indentation_levels[indent] += 1
            else:
                indentation_levels[indent] = 1

    # Should have at least 3 different indentation levels for complex nested cases
    assert len(indentation_levels) >= 3

    # Parse the original and merged files to ensure content was preserved correctly
    local_parsed = _parse_conf_file(local_dir / "splunk_transforms.conf")
    merged_parsed = _parse_conf_file(default_dir / "splunk_transforms.conf")

    # Check a deeply nested stanza
    assert (
        local_parsed["severity_calculation"]["INGEST_EVAL"]
        == merged_parsed["severity_calculation"]["INGEST_EVAL"]
    )

    # Check a stanza with embedded comments
    assert (
        local_parsed["custom_log_extraction"]["REGEX"]
        == merged_parsed["custom_log_extraction"]["REGEX"]
    )
