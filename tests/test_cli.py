"""Tests for CLI functionality."""

import pytest
from pathlib import Path
from bydefault.cli import main


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
    """.strip()
    )

    app_conf = default_dir / "app.conf"
    app_conf.write_text(
        """
[launcher]
version = 1.0.0
    """.strip()
    )

    return tmp_path


def test_main_no_args():
    """Test CLI with no arguments."""
    result = main([])
    assert result == 1


def test_main_invalid_command():
    """Test CLI with invalid command."""
    result = main(["invalid"])
    assert result == 1


def test_merge_command(temp_ta_structure, monkeypatch):
    """Test merge command."""
    monkeypatch.chdir(temp_ta_structure)
    result = main(["merge"])
    assert result == 0


def test_version_command_no_version(temp_ta_structure, monkeypatch):
    """Test version command without version argument."""
    monkeypatch.chdir(temp_ta_structure)
    result = main(["version"])
    assert result == 1


def test_version_command(temp_ta_structure, monkeypatch):
    """Test version command."""
    monkeypatch.chdir(temp_ta_structure)
    result = main(["version", "2.0.0"])
    assert result == 0


def test_merge_command_no_local_configs(tmp_path, monkeypatch):
    """Test merge command with no local configurations."""
    monkeypatch.chdir(tmp_path)
    result = main(["merge"])
    assert result == 1  # Should fail because no TA structure exists
