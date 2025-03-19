"""Tests for change detection functionality.

This module contains tests for the change detection logic used in the scan command.
"""

import tempfile
from pathlib import Path

from bydefault.utils.change_detection import (
    _is_stanza_header,
    _parse_conf_file,
    detect_stanza_changes,
)


def test_is_stanza_header():
    """Test that the stanza header detection works correctly."""
    # Standard stanza headers
    assert _is_stanza_header("[stanza1]") is True
    assert _is_stanza_header("  [stanza2]  ") is True

    # Not stanza headers
    assert _is_stanza_header("key = value") is False
    assert _is_stanza_header("# comment") is False
    assert _is_stanza_header("") is False

    # Command contexts (should not be detected as stanza headers)
    assert (
        _is_stanza_header(
            '| foreach mode=multivalue employees [eval employees_array=json_append(employees_array, "", <<ITEM>>)]'
        )
        is False
    )
    assert _is_stanza_header("| search [index=main source=*]") is False

    # Line continuation context
    assert _is_stanza_header("[not_a_stanza]", "key = value \\") is False

    # Command syntax within brackets
    assert _is_stanza_header("[index=main | stats count]") is False


def test_parse_conf_file_with_commands():
    """Test that the conf file parser correctly handles command contexts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test conf file with command contexts
        conf_path = Path(temp_dir) / "test.conf"
        with open(conf_path, "w") as f:
            f.write("""
[stanza1]
key1 = value1
key2 = value2

[stanza2]
search = | search index=main source=*
command = | foreach mode=multivalue employees [eval employees_array=json_append(employees_array, "", <<ITEM>>)]

# This is a multiline search with square brackets that should not be detected as stanzas
[stanza3]
# Using a proper multiline format with continuation characters
multiline_search = this is a test search with brackets \\
    continued on a second line with [bracketed content] \\
    and finally a third line

# This is a real stanza after the multiline content
[stanza4]
key = value
            """)

        # Parse the conf file
        stanzas = _parse_conf_file(conf_path)

        # Check that the correct stanzas were detected
        assert set(stanzas.keys()) == {"stanza1", "stanza2", "stanza3", "stanza4"}

        # Check that multiline values are correctly parsed
        expected_multiline = "this is a test search with brackets continued on a second line with [bracketed content] and finally a third line"
        # The actual value might have different spacing, so we normalize it
        actual_multiline = stanzas["stanza3"]["multiline_search"].replace("  ", " ")
        # Remove extra spaces for comparison
        expected_multiline = " ".join(expected_multiline.split())
        actual_multiline = " ".join(actual_multiline.split())
        assert actual_multiline == expected_multiline


def test_detect_stanza_changes_with_commands():
    """Test that stanza changes are correctly detected even with command contexts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create base file with command contexts
        base_file = Path(temp_dir) / "base.conf"
        with open(base_file, "w") as f:
            f.write("""
[stanza1]
key1 = value1
key2 = value2

[stanza2]
search = | search index=main source=*
command = | foreach mode=multivalue employees [eval employees_array=json_append(employees_array, "", <<ITEM>>)]
            """)

        # Create current file with changes including command contexts
        current_file = Path(temp_dir) / "current.conf"
        with open(current_file, "w") as f:
            f.write("""
[stanza1]
key1 = value1-modified
key2 = value2

[stanza2]
search = | search index=main source=* sourcetype=xyz
command = | foreach mode=multivalue employees [eval employees_array=json_append(employees_array, "", <<ITEM>>)]

# This is a search with square brackets and multiline format
[stanza3]
multiline_search = this is a test search with \\
    brackets [in the content] that continues \\
    across multiple lines
            """)

        # Detect stanza changes
        changes = detect_stanza_changes(base_file, current_file)

        # Check that the correct changes were detected - all three are valid
        assert len(changes) == 3  # stanza1 modified, stanza2 modified, stanza3 added

        # Find the stanza1 change
        stanza1_change = next((c for c in changes if c.name == "stanza1"), None)
        assert stanza1_change is not None
        assert stanza1_change.change_type.value == "modified"

        # Find the stanza2 change
        stanza2_change = next((c for c in changes if c.name == "stanza2"), None)
        assert stanza2_change is not None
        assert stanza2_change.change_type.value == "modified"

        # Find the stanza3 change (added)
        stanza3_change = next((c for c in changes if c.name == "stanza3"), None)
        assert stanza3_change is not None
        assert stanza3_change.change_type.value == "added"

        # Verify stanza3 contains the complete multiline value
        multiline_value = stanza3_change.setting_changes[0].local_value
        assert (
            "brackets [in the content] that continues across multiple lines"
            in " ".join(multiline_value.split())
        )

        # Verify no false stanza was detected
        not_a_stanza = next(
            (c for c in changes if c.name == "not_a_stanza_header"), None
        )
        assert not_a_stanza is None
