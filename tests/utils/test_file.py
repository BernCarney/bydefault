"""Tests for file utility functions."""

from pathlib import Path

import pytest

from bydefault.utils.file import (
    InvalidWorkingDirectoryError,
    find_conf_files,
    find_git_root,
    find_ta_directories,
    get_local_conf_files,
    is_ta_directory,
    match_conf_files,
    validate_working_context,
)


@pytest.fixture
def git_repo_dir(tmp_path: Path) -> Path:
    """Create a mock git repository with TAs."""
    repo_dir = tmp_path / "git_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    # Create a valid TA
    ta_dir = repo_dir / "TA-test"
    ta_dir.mkdir()
    (ta_dir / "local").mkdir()
    (ta_dir / "default").mkdir()
    (ta_dir / "default" / "app.conf").touch()

    return repo_dir


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


def test_validate_working_context_in_ta(sample_ta_dir: Path) -> None:
    """Test working context validation when inside a TA directory."""
    # Create required structure for a valid TA
    (sample_ta_dir / "default" / "app.conf").touch()

    result = validate_working_context(sample_ta_dir)
    assert result == sample_ta_dir


def test_validate_working_context_in_ta_parent(sample_ta_dir: Path) -> None:
    """Test working context validation when in directory containing TAs."""
    # Create required structure for a valid TA
    (sample_ta_dir / "default" / "app.conf").touch()

    result = validate_working_context(sample_ta_dir.parent)
    assert result == sample_ta_dir.parent


def test_validate_working_context_in_git_repo(git_repo_dir: Path) -> None:
    """Test working context validation when in git repository with TAs."""
    result = validate_working_context(git_repo_dir)
    assert result == git_repo_dir


def test_validate_working_context_invalid(tmp_path: Path) -> None:
    """Test working context validation fails in invalid directory."""
    with pytest.raises(InvalidWorkingDirectoryError) as exc:
        validate_working_context(tmp_path)
    assert "Not in a valid working directory" in str(exc.value)


def test_find_git_root(git_repo_dir: Path) -> None:
    """Test finding git repository root."""
    # Test from repo root
    assert find_git_root(git_repo_dir) == git_repo_dir

    # Test from subdirectory
    subdir = git_repo_dir / "subdir"
    subdir.mkdir()
    assert find_git_root(subdir) == git_repo_dir


def test_find_git_root_not_in_repo(tmp_path: Path) -> None:
    """Test finding git root when not in a repository."""
    assert find_git_root(tmp_path) is None


def test_find_ta_directories(git_repo_dir: Path) -> None:
    """Test finding TA directories in a root path."""
    tas = find_ta_directories(git_repo_dir)
    assert len(tas) == 1
    assert tas[0].name == "TA-test"


def test_find_ta_directories_no_tas(tmp_path: Path) -> None:
    """Test finding TA directories when none exist."""
    with pytest.raises(InvalidWorkingDirectoryError) as exc:
        find_ta_directories(tmp_path)
    assert "No valid TA directories found" in str(exc.value)
