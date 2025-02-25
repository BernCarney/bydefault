"""Tests for the scanner module."""

from pathlib import Path

import pytest

from bydefault.utils.scanner import find_tas, is_valid_ta


@pytest.fixture
def mock_ta_directory(tmp_path):
    """Create a mock TA directory structure.

    Creates a temporary directory with a valid TA structure:
    - default/app.conf
    - default/props.conf
    """
    ta_dir = tmp_path / "test_ta"
    default_dir = ta_dir / "default"
    default_dir.mkdir(parents=True)

    # Create app.conf
    app_conf = default_dir / "app.conf"
    app_conf.write_text("[launcher]\nversion = 1.0.0\n")

    # Create props.conf
    props_conf = default_dir / "props.conf"
    props_conf.write_text("[test_sourcetype]\nDISABLE_KV_TRIMMING = 0\n")

    return ta_dir


@pytest.fixture
def mock_ta_no_app_conf(tmp_path):
    """Create a mock TA directory without app.conf but with other .conf files."""
    ta_dir = tmp_path / "test_ta_no_app"
    default_dir = ta_dir / "default"
    default_dir.mkdir(parents=True)

    # Create props.conf only
    props_conf = default_dir / "props.conf"
    props_conf.write_text("[test_sourcetype]\nDISABLE_KV_TRIMMING = 0\n")

    return ta_dir


@pytest.fixture
def mock_invalid_directory(tmp_path):
    """Create a directory that is not a valid TA."""
    invalid_dir = tmp_path / "invalid_dir"
    invalid_dir.mkdir()
    # Create a random file
    test_file = invalid_dir / "test.txt"
    test_file.write_text("This is not a TA")
    return invalid_dir


@pytest.fixture
def mock_multiple_tas(tmp_path):
    """Create a directory containing multiple TAs."""
    root_dir = tmp_path / "multiple_tas"
    root_dir.mkdir()

    # Create TA1
    ta1_dir = root_dir / "ta1"
    ta1_default = ta1_dir / "default"
    ta1_default.mkdir(parents=True)
    (ta1_default / "app.conf").write_text("[launcher]\nversion = 1.0.0\n")

    # Create TA2
    ta2_dir = root_dir / "ta2"
    ta2_default = ta2_dir / "default"
    ta2_default.mkdir(parents=True)
    (ta2_default / "props.conf").write_text("[test]\nKEY = value\n")

    # Create a non-TA directory
    non_ta = root_dir / "not_a_ta"
    non_ta.mkdir()
    (non_ta / "random.txt").write_text("Not a TA")

    # Create a nested TA in a subdirectory
    nested_dir = root_dir / "nested"
    nested_dir.mkdir()
    nested_ta = nested_dir / "nested_ta"
    nested_ta_default = nested_ta / "default"
    nested_ta_default.mkdir(parents=True)
    (nested_ta_default / "app.conf").write_text("[launcher]\nversion = 1.0.0\n")

    return root_dir


class TestTADetection:
    """Tests for TA detection functionality."""

    def test_is_valid_ta_with_app_conf(self, mock_ta_directory):
        """Test that a directory with default/app.conf is recognized as a valid TA."""
        assert is_valid_ta(mock_ta_directory) is True

    def test_is_valid_ta_without_app_conf(self, mock_ta_no_app_conf):
        """Test that a directory with default/*.conf but no app.conf is still valid."""
        assert is_valid_ta(mock_ta_no_app_conf) is True

    def test_is_valid_ta_invalid_directory(self, mock_invalid_directory):
        """Test that a directory without default/ is not a valid TA."""
        assert is_valid_ta(mock_invalid_directory) is False

    def test_is_valid_ta_non_existent(self, tmp_path):
        """Test that a non-existent path is not a valid TA."""
        non_existent = tmp_path / "does_not_exist"
        assert is_valid_ta(non_existent) is False

    def test_is_valid_ta_empty_default(self, tmp_path):
        """Test that a directory with empty default/ is not a valid TA."""
        ta_dir = tmp_path / "empty_ta"
        default_dir = ta_dir / "default"
        default_dir.mkdir(parents=True)
        assert is_valid_ta(ta_dir) is False

    def test_is_valid_ta_file_path(self, tmp_path):
        """Test that a file path is not a valid TA."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Not a TA")
        assert is_valid_ta(test_file) is False


class TestFindTAs:
    """Tests for find_tas function."""

    def test_find_tas_direct(self, mock_ta_directory):
        """Test finding a TA when the path is directly a TA."""
        tas = find_tas(mock_ta_directory)
        assert len(tas) == 1
        assert tas[0] == mock_ta_directory

    def test_find_tas_parent_directory(self, mock_multiple_tas):
        """Test finding TAs in direct children of a directory."""
        tas = find_tas(mock_multiple_tas)
        assert len(tas) == 2  # Should find ta1 and ta2 but not the nested one
        assert any(ta.name == "ta1" for ta in tas)
        assert any(ta.name == "ta2" for ta in tas)
        # Should not find the nested TA without recursive
        assert not any("nested_ta" in str(ta) for ta in tas)

    def test_find_tas_recursive(self, mock_multiple_tas):
        """Test finding TAs recursively."""
        tas = find_tas(mock_multiple_tas, recursive=True)
        assert len(tas) == 3  # Should find all 3 TAs
        assert any(ta.name == "ta1" for ta in tas)
        assert any(ta.name == "ta2" for ta in tas)
        assert any(ta.name == "nested_ta" for ta in tas)

    def test_find_tas_non_existent(self):
        """Test that find_tas raises FileNotFoundError for non-existent paths."""
        with pytest.raises(FileNotFoundError):
            find_tas(Path("/path/does/not/exist"))

    def test_find_tas_file_path(self, tmp_path):
        """Test that find_tas raises NotADirectoryError for file paths."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Not a directory")
        with pytest.raises(NotADirectoryError):
            find_tas(test_file)

    def test_find_tas_empty_directory(self, tmp_path):
        """Test that find_tas returns an empty list for directories with no TAs."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        tas = find_tas(empty_dir)
        assert len(tas) == 0

    def test_find_tas_error_handling(self, tmp_path, monkeypatch):
        """Test that find_tas handles errors in subdirectories gracefully."""
        # Create a directory structure
        root = tmp_path / "root"
        root.mkdir()
        sub = root / "sub"
        sub.mkdir()

        # Create a valid TA
        ta_dir = root / "valid_ta"
        default_dir = ta_dir / "default"
        default_dir.mkdir(parents=True)
        (default_dir / "app.conf").write_text("[launcher]\nversion = 1.0.0\n")

        # Simulate a permission error when accessing the subdirectory
        def mock_iterdir_error(self):
            if self.name == "sub":
                raise PermissionError("Permission denied")
            return orig_iterdir(self)

        orig_iterdir = Path.iterdir
        monkeypatch.setattr(Path, "iterdir", mock_iterdir_error)

        # Should still find the valid TA and not crash on the error
        tas = find_tas(root, recursive=True)
        assert len(tas) == 1
        assert tas[0].name == "valid_ta"
