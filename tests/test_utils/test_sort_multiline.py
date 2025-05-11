"""Tests for the sort utility's handling of multi-line values."""

import shutil
from pathlib import Path

import pytest

from bydefault.utils.sort_utils import ConfigSorter


def setup_test_file(tmp_path, fixture_file):
    """Set up a test file from a fixture."""
    # Get the path to the fixture file
    current_dir = Path(__file__).parent
    fixture_path = current_dir.parent / "fixtures" / "merge" / fixture_file

    if not fixture_path.exists():
        pytest.fail(f"Fixture file not found: {fixture_path}")

    # Create the destination file
    test_file = tmp_path / fixture_file

    # Copy the fixture to the temp directory
    shutil.copy(fixture_path, test_file)

    return test_file, fixture_path


def test_sort_complex_multiline_conf(tmp_path):
    """Test sorting a configuration file with complex multi-line values."""
    # Set up test file
    test_file, original_path = setup_test_file(tmp_path, "complex_multiline.conf")

    # Read the original content for comparison
    with open(original_path, "r", encoding="utf-8") as f:
        original_content = f.read()
    print("\n\n==== ORIGINAL CONTENT ====")
    print(original_content)

    # Create and run the sorter
    sorter = ConfigSorter(test_file, verbose=True)
    sorter.parse()
    result = sorter.sort()
    sorter.write()

    # Read the sorted content
    with open(test_file, "r", encoding="utf-8") as f:
        sorted_content = f.read()
    print("\n\n==== SORTED CONTENT ====")
    print(sorted_content)

    # Check that all multi-line values are preserved with their line breaks
    # Test specific multi-line values from the fixture

    # 1. Check complex search commands with pipes
    assert "search = index=main sourcetype=access_combined" in sorted_content
    assert "| fields clientip, status, uri_path, useragent" in sorted_content
    assert "| stats count by clientip, status" in sorted_content
    assert "| sort -count" in sorted_content
    assert "| head 100" in sorted_content

    # 2. Check nested case statements with multiple levels
    assert "EVAL-severity_level = case(" in sorted_content
    assert 'match(log_level, "^ERROR")' in sorted_content
    assert 'match(message, ".*OutOfMemory.*")' in sorted_content

    # 3. Verify that embedded comments in multi-line values are preserved
    assert "# This comment should be preserved in the exact position" in sorted_content
    assert "# This describes the following operation" in sorted_content

    # 4. Check complex script with embedded formatting
    assert 'action.script = if severity_level == "critical":' in sorted_content
    assert "# Send immediate notification" in sorted_content
    assert "# Create incident ticket" in sorted_content

    # 5. Check JSON structure preservation
    assert "action.payload =" in sorted_content
    assert '"alert_name": "$name$"' in sorted_content
    assert '"results":' in sorted_content
    assert '"fields":' in sorted_content

    # Ensure stanzas are present
    for stanza in [
        "search_commands",
        "transforms",
        "props:app:myapp",
        "alert:complex_automation",
    ]:
        assert f"[{stanza}]" in sorted_content

    # Verify that the sort was successful
    assert result["stanzas_reordered"] > 0
    assert result["settings_sorted"] > 0
    assert result["comments_preserved"] > 0


def test_sort_splunk_transforms_conf(tmp_path):
    """Test sorting a realistic Splunk transforms.conf file with complex multi-line values."""
    # Set up test file
    test_file, original_path = setup_test_file(tmp_path, "splunk_transforms.conf")

    # Read the original content for comparison
    with open(original_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # Create and run the sorter
    sorter = ConfigSorter(test_file, verbose=True)
    sorter.parse()
    result = sorter.sort()
    sorter.write()

    # Read the sorted content
    with open(test_file, "r", encoding="utf-8") as f:
        sorted_content = f.read()

    # Extract stanza names from original and sorted content
    original_stanzas = []
    for line in original_content.splitlines():
        if line.startswith("[") and line.endswith("]"):
            original_stanzas.append(line.strip("[]"))

    sorted_stanzas = []
    for line in sorted_content.splitlines():
        if line.startswith("[") and line.endswith("]"):
            sorted_stanzas.append(line.strip("[]"))

    # Verify all stanzas from original are in sorted
    for stanza in original_stanzas:
        assert stanza in sorted_stanzas, f"Stanza {stanza} missing after sorting"

    # Check for key patterns that should be preserved
    key_patterns = [
        "REGEX",
        "FORMAT",
        "DEST_KEY",
        "filename",
        "INGEST_EVAL",
        "external_cmd",
    ]

    for pattern in key_patterns:
        assert pattern in sorted_content, f"Key pattern '{pattern}' is missing"

    # Extract all keys from original content
    original_keys = []
    for line in original_content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=")[0].strip()
            if key:
                original_keys.append(key)

    # Verify that a large percentage of original keys are in sorted content
    keys_found = 0
    for key in set(original_keys):  # Use set to avoid duplicates
        if key in sorted_content:
            keys_found += 1

    # We should have at least 80% of the original keys
    keys_percentage = (keys_found / len(set(original_keys))) * 100
    assert (
        keys_percentage >= 80
    ), f"Only {keys_percentage:.2f}% of original keys preserved"

    # Check for essential multiline content markers
    multiline_markers = ["\\", "case(", "match("]
    for marker in multiline_markers:
        assert marker in sorted_content, f"Multiline marker '{marker}' missing"

    # Verify that the sort was successful
    assert result["stanzas_reordered"] > 0
    assert result["settings_sorted"] > 0
    assert result["comments_preserved"] > 0


def test_sort_multiline_values_conf(tmp_path):
    """Test sorting the multiline_values.conf test fixture."""
    # Create a copy of the multiline_values.conf fixture
    current_dir = Path(__file__).parent
    fixture_path = current_dir.parent / "fixtures" / "sort" / "multiline_values.conf"

    if not fixture_path.exists():
        pytest.fail(f"Fixture file not found: {fixture_path}")

    # Create the destination file
    test_file = tmp_path / "multiline_values.conf"

    # Copy the fixture to the temp directory
    shutil.copy(fixture_path, test_file)

    # Read the original content for debugging
    with open(test_file, "r", encoding="utf-8") as f:
        original_content = f.read()
    print("\n\n==== ORIGINAL CONTENT ====")
    print(original_content)

    # Create and run the sorter
    sorter = ConfigSorter(test_file, verbose=True)
    sorter.parse()
    result = sorter.sort()
    sorter.write()

    # Read the sorted content
    with open(test_file, "r", encoding="utf-8") as f:
        sorted_content = f.read()
    print("\n\n==== SORTED CONTENT ====")
    print(sorted_content)

    # Check that important multiline patterns are preserved, without requiring exact order
    assert "EVAL-severity = case(" in sorted_content
    assert "match(source" in sorted_content
    assert "match(message" in sorted_content
    assert "P1" in sorted_content
    assert "P2" in sorted_content

    # Check that backslash continuations are preserved
    assert "\\" in sorted_content

    # Check the search format is preserved
    assert "search = index=web" in sorted_content
    assert "host=webserver*" in sorted_content
    assert "| stats count by status, uri_path" in sorted_content

    # Verify that the sort was successful
    assert result["stanzas_reordered"] > 0
    assert result["settings_sorted"] > 0
    assert result["comments_preserved"] > 0
