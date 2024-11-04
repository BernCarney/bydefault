"""Tests for file utility functions."""

from pathlib import Path

from bydefault.utils.file import (
    find_conf_files,
    get_local_conf_files,
    is_ta_directory,
    match_conf_files,
)


def test_find_conf_files_empty_dir(sample_ta_dir: Path) -> None:
    """Test finding conf files in empty directory."""
    files = list(find_conf_files(sample_ta_dir))
    assert len(files) == 0


def test_find_conf_files_with_files(sample_ta_dir: Path) -> None:
    """Test finding conf files in directory with files."""
    # Create test files
    (sample_ta_dir / "local" / "props.conf").touch()
    (sample_ta_dir / "local" / "transforms.conf").touch()
    (sample_ta_dir / "local" / "not_a_conf.txt").touch()

    files = list(find_conf_files(sample_ta_dir))
    assert len(files) == 2
    assert all(f.suffix == ".conf" for f in files)


def test_get_local_conf_files(sample_ta_dir: Path) -> None:
    """Test getting local conf files."""
    # Create test files
    (sample_ta_dir / "local" / "props.conf").touch()
    (sample_ta_dir / "local" / "transforms.conf").touch()
    (sample_ta_dir / "default" / "props.conf").touch()  # Should not be included

    files = get_local_conf_files(sample_ta_dir)
    assert len(files) == 2
    assert all(f.parent.name == "local" for f in files)


def test_match_conf_files(sample_ta_dir: Path) -> None:
    """Test matching conf files between local and default."""
    # Create test files
    (sample_ta_dir / "local" / "props.conf").touch()
    (sample_ta_dir / "local" / "transforms.conf").touch()
    (sample_ta_dir / "default" / "props.conf").touch()

    matches = match_conf_files(sample_ta_dir)
    assert len(matches) == 2

    local_props = sample_ta_dir / "local" / "props.conf"
    local_transforms = sample_ta_dir / "local" / "transforms.conf"

    assert matches[local_props] is not None  # Has default counterpart
    assert matches[local_transforms] is None  # No default counterpart


def test_is_ta_directory(sample_ta_dir: Path) -> None:
    """Test TA directory validation."""
    assert not is_ta_directory(sample_ta_dir)  # Missing app.conf

    # Create required structure
    (sample_ta_dir / "default" / "app.conf").touch()
    assert is_ta_directory(sample_ta_dir)
