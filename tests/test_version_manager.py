"""Tests for version management."""

import pytest
from pathlib import Path
from bydefault.core import version_manager


@pytest.fixture
def temp_ta_structure(tmp_path):
    """Create a temporary TA structure for testing."""
    ta_root = tmp_path / "TA-test"
    default_dir = ta_root / "default"
    default_dir.mkdir(parents=True)

    app_conf = default_dir / "app.conf"
    app_conf.write_text(
        """
[launcher]
version = 1.0.0
author = Test Author

[package]
id = TA-test
    """.strip()
    )

    return ta_root


def test_read_ta_version(temp_ta_structure):
    """Test reading TA version."""
    version = version_manager.read_ta_version(temp_ta_structure)
    assert version == "1.0.0"


def test_update_ta_version(temp_ta_structure):
    """Test updating TA version."""
    success = version_manager.update_ta_version(temp_ta_structure, "2.0.0")
    assert success

    # Verify update
    version = version_manager.read_ta_version(temp_ta_structure)
    assert version == "2.0.0"


def test_find_tas(tmp_path):
    """Test finding TAs in directory."""
    # Create test TAs
    ta1 = tmp_path / "TA-test1"
    ta2 = tmp_path / "TA-test2"
    not_ta = tmp_path / "NOT-TA"

    for ta in [ta1, ta2, not_ta]:
        (ta / "default").mkdir(parents=True)
        (ta / "default" / "app.conf").touch()

    tas = version_manager.find_tas(tmp_path)
    assert len(tas) == 2
    assert ta1 in tas
    assert ta2 in tas
    assert not_ta not in tas
