"""Tests for file utility functions."""

from pathlib import Path

import pytest

from bydefault.utils.file import find_conf_files


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


def test_find_conf_files_pattern(sample_ta_dir: Path) -> None:
    """Test finding files with custom pattern."""
    (sample_ta_dir / "test.meta").touch()

    files = list(find_conf_files(sample_ta_dir, "*.meta"))
    assert len(files) == 1
    assert files[0].name == "test.meta"


def test_find_conf_files_invalid_dir() -> None:
    """Test finding files in non-existent directory."""
    with pytest.raises(FileNotFoundError):
        list(find_conf_files(Path("non_existent_dir")))
