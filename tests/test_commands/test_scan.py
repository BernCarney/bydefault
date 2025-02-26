"""Tests for the scan command functionality."""

import shutil
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import MagicMock, Mock, patch

from rich.console import Console

from bydefault.commands.scan import (
    _display_results,
    add_subparser,
    handle_scan_command,
    scan_command,
)
from bydefault.models.change_detection import (
    ChangeType,
    FileChange,
    ScanResult,
    StanzaChange,
)


class TestScanCommand(TestCase):
    """Test case for scan command functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.test_dir = Path(tempfile.mkdtemp())
        self.ta_dir = self.test_dir / "test_ta"
        self.baseline_dir = self.test_dir / "baseline_ta"

        # Create TA directory structure
        self._create_ta_structure(self.ta_dir)
        self._create_ta_structure(self.baseline_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_ta_structure(self, path: Path):
        """Create a basic TA directory structure for testing."""
        # Create directories
        path.mkdir(exist_ok=True)
        (path / "default").mkdir(exist_ok=True)
        (path / "local").mkdir(exist_ok=True)
        (path / "metadata").mkdir(exist_ok=True)

        # Create a minimal app.conf
        with open(path / "default" / "app.conf", "w") as f:
            f.write("[install]\n")
            f.write("state = enabled\n")
            f.write("\n")
            f.write("[package]\n")
            f.write("id = test_app\n")
            f.write("check_for_updates = 1\n")

    @patch("bydefault.commands.scan.Console")
    @patch("bydefault.commands.scan.find_tas")
    @patch("bydefault.commands.scan.is_valid_ta")
    @patch("bydefault.commands.scan.scan_directory")
    @patch("bydefault.commands.scan._display_results")
    def test_scan_command_with_valid_paths(
        self, mock_display, mock_scan_dir, mock_is_valid, mock_find_tas, mock_console
    ):
        """Test scan command with valid paths."""
        # Setup mocks
        mock_is_valid.return_value = True
        mock_scan_dir.return_value = MagicMock(spec=ScanResult)

        # Call the function
        result = scan_command([str(self.ta_dir)])

        # Verify the result
        self.assertEqual(result, 0)
        mock_is_valid.assert_called_once_with(mock.ANY)
        mock_scan_dir.assert_called_once()
        mock_display.assert_called_once()
        mock_find_tas.assert_not_called()  # Should not be called since path is a valid TA

    @patch("bydefault.commands.scan.Console")
    @patch("bydefault.commands.scan.find_tas")
    @patch("bydefault.commands.scan.is_valid_ta")
    @patch("bydefault.commands.scan.scan_directory")
    @patch("bydefault.commands.scan._display_results")
    def test_scan_command_with_directory_containing_tas(
        self, mock_display, mock_scan_dir, mock_is_valid, mock_find_tas, mock_console
    ):
        """Test scan command with a directory containing TAs."""
        # Setup mocks
        mock_is_valid.return_value = False  # Not a valid TA itself
        mock_find_tas.return_value = [self.ta_dir, self.baseline_dir]
        mock_scan_dir.return_value = MagicMock(spec=ScanResult)

        # Call the function
        result = scan_command([str(self.test_dir)], recursive=True)

        # Verify the result
        self.assertEqual(result, 0)
        mock_is_valid.assert_called_once_with(mock.ANY)
        mock_find_tas.assert_called_once_with(mock.ANY, recursive=True)
        self.assertEqual(mock_scan_dir.call_count, 2)  # Called for each found TA
        mock_display.assert_called_once()

    @patch("bydefault.commands.scan.Console")
    def test_scan_command_with_invalid_path(self, mock_console):
        """Test scan command with an invalid path."""
        # Call the function with a non-existent path
        result = scan_command(["/non/existent/path"])

        # Verify the result
        self.assertEqual(result, 1)
        mock_console().print.assert_called_with(
            "[red]Error: No valid paths provided[/red]"
        )

    @patch("bydefault.commands.scan.Console")
    @patch("bydefault.commands.scan.is_valid_ta")
    def test_scan_command_with_invalid_baseline(self, mock_is_valid, mock_console):
        """Test scan command with an invalid baseline path."""
        # Setup mocks
        mock_is_valid.return_value = False

        # Call the function with a valid path but invalid baseline
        result = scan_command([str(self.ta_dir)], baseline=str(self.test_dir))

        # Verify the result
        self.assertEqual(result, 1)
        mock_console().print.assert_called_with(mock.ANY)  # Called with error message

    @patch("bydefault.commands.scan.Console")
    @patch("bydefault.commands.scan.find_tas")
    @patch("bydefault.commands.scan.is_valid_ta")
    def test_scan_command_with_no_tas_found(
        self, mock_is_valid, mock_find_tas, mock_console
    ):
        """Test scan command when no TAs are found."""
        # Setup mocks
        mock_is_valid.return_value = False  # Not a valid TA itself
        mock_find_tas.return_value = []  # No TAs found

        # Call the function
        result = scan_command([str(self.test_dir)])

        # Verify the result
        self.assertEqual(result, 0)
        mock_console().print.assert_called_with(
            "[yellow]No Splunk TAs found in the specified paths[/yellow]"
        )

    @patch("bydefault.commands.scan.Console")
    @patch("bydefault.commands.scan.find_tas")
    @patch("bydefault.commands.scan.is_valid_ta")
    @patch("bydefault.commands.scan.scan_directory")
    def test_scan_command_with_error_during_scan(
        self, mock_scan_dir, mock_is_valid, mock_find_tas, mock_console
    ):
        """Test scan command when an error occurs during scanning."""
        # Setup mocks
        mock_is_valid.return_value = True
        mock_scan_dir.side_effect = Exception("Test error")

        # Call the function
        result = scan_command([str(self.ta_dir)])

        # Verify the result
        self.assertEqual(result, 0)  # Still returns 0 as this is not a fatal error
        mock_console().print.assert_any_call(
            f"[red]Error scanning {self.ta_dir}: Test error[/red]"
        )  # Called with error message


class TestDisplayResults(TestCase):
    """Test case for display_results functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = MagicMock()
        # Create temporary directories
        self.test_dir = Path(tempfile.mkdtemp())
        self.ta_dir = self.test_dir / "test_ta"
        self.baseline_dir = self.test_dir / "baseline_ta"

        # Create TA directory structure
        self._create_ta_structure(self.ta_dir)
        self._create_ta_structure(self.baseline_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_ta_structure(self, path: Path):
        """Create a basic TA directory structure for testing."""
        # Create directories
        path.mkdir(exist_ok=True)
        (path / "default").mkdir(exist_ok=True)
        (path / "local").mkdir(exist_ok=True)
        (path / "metadata").mkdir(exist_ok=True)

        # Create a minimal app.conf
        with open(path / "default" / "app.conf", "w") as f:
            f.write("[install]\n")
            f.write("state = enabled\n")
            f.write("\n")
            f.write("[package]\n")
            f.write("id = test_app\n")
            f.write("check_for_updates = 1\n")

    @patch("bydefault.commands.scan._display_results")
    def test_display_results_summary_mode(self, mock_display):
        """Test display_results in summary mode."""
        # Create mock scan results
        scan_results = [
            MagicMock(
                ta_path=self.ta_dir,
                is_valid_ta=True,
                error_message=None,
                file_changes=[
                    MagicMock(is_new=True, stanza_changes=[]),
                    MagicMock(is_new=False, stanza_changes=[]),
                ],
            )
        ]

        # Call scan_command to trigger _display_results
        scan_command([str(self.ta_dir)], summary=True)

        # Verify _display_results was called with summary=True
        mock_display.assert_called_once()
        args, kwargs = mock_display.call_args
        self.assertTrue(args[2])  # summary flag

    @patch("bydefault.commands.scan._display_results")
    def test_display_results_details_mode(self, mock_display):
        """Test display_results in details mode."""
        # Create mock scan results
        scan_results = [
            MagicMock(
                ta_path=self.ta_dir,
                is_valid_ta=True,
                error_message=None,
                file_changes=[
                    MagicMock(is_new=True, stanza_changes=[]),
                    MagicMock(is_new=False, stanza_changes=[]),
                ],
            )
        ]

        # Call scan_command to trigger _display_results
        scan_command([str(self.ta_dir)], details=True)

        # Verify _display_results was called with details=True
        mock_display.assert_called_once()
        args, kwargs = mock_display.call_args
        self.assertTrue(args[3])  # details flag


class TestDisplayResultsFunction(TestCase):
    """Test case for the _display_results function directly."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = Mock(spec=Console)
        self.test_dir = Path(tempfile.mkdtemp())
        self.ta_dir = self.test_dir / "test_ta"

    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_display_results_invalid_ta(self):
        """Test displaying results for an invalid TA."""
        # Create a scan result for an invalid TA
        scan_results = [
            ScanResult(
                ta_path=self.ta_dir,
                file_changes=[],
                is_valid_ta=False,
                error_message=None,
            )
        ]

        # Call the function
        _display_results(self.console, scan_results, False, True)

        # Verify console.print was called
        self.console.print.assert_any_call(f"{self.ta_dir.name}: Not a valid Splunk TA")

    def test_display_results_with_error(self):
        """Test displaying results with an error message."""
        # Create a scan result with an error message
        scan_results = [
            ScanResult(
                ta_path=self.ta_dir,
                file_changes=[],
                is_valid_ta=True,
                error_message="Test error message",
            )
        ]

        # Call the function
        _display_results(self.console, scan_results, False, True)

        # Verify console.print was called
        self.console.print.assert_any_call(f"{self.ta_dir.name}: Test error message")

    def test_display_results_no_changes(self):
        """Test displaying results with no changes."""
        # Create a scan result with no changes
        scan_results = [
            ScanResult(
                ta_path=self.ta_dir,
                file_changes=[],
                is_valid_ta=True,
                error_message=None,
            )
        ]

        # Call the function
        _display_results(self.console, scan_results, False, True)

        # Verify console.print was called
        self.console.print.assert_any_call(
            f"No changes detected in: {self.ta_dir.name}"
        )

    def test_display_results_with_changes_summary(self):
        """Test displaying results with changes in summary mode."""
        # Create a file change with added and removed files
        file_changes = [
            FileChange(file_path=Path("default/app.conf"), is_new=True),
            FileChange(file_path=Path("default/inputs.conf"), is_new=False),
        ]

        # Create a scan result with changes
        scan_results = [
            ScanResult(
                ta_path=self.ta_dir,
                file_changes=file_changes,
                is_valid_ta=True,
                error_message=None,
            )
        ]

        # Call the function in summary mode
        _display_results(self.console, scan_results, True, False)

        # Verify console.print was called with the right arguments
        self.console.print.assert_any_call(f"Changes detected in: {self.ta_dir.name}")
        self.console.print.assert_any_call(mock.ANY)  # Table object

    def test_display_results_with_changes_details(self):
        """Test displaying results with changes in detail mode."""
        # Create a stanza change
        stanza_change = StanzaChange(
            name="package",
            change_type=ChangeType.MODIFIED,
        )
        stanza_change.add_setting_change(
            name="check_for_updates",
            change_type=ChangeType.MODIFIED,
            local_value="0",
            default_value="1",
        )

        # Create file changes with stanza changes
        file_changes = [
            FileChange(
                file_path=Path("default/app.conf"),
                is_new=False,
                stanza_changes=[stanza_change],
            )
        ]

        # Create a scan result with changes
        scan_results = [
            ScanResult(
                ta_path=self.ta_dir,
                file_changes=file_changes,
                is_valid_ta=True,
                error_message=None,
            )
        ]

        # Call the function in detail mode
        _display_results(self.console, scan_results, False, True)

        # Verify console.print was called with the right arguments
        self.console.print.assert_any_call(f"Changes detected in: {self.ta_dir.name}")

        # Assert that a Text object with the right style was passed to console.print
        # We can use mock.ANY for the Text object and check that it has the right style
        any_call_found = False
        for call in self.console.print.call_args_list:
            args, _ = call
            if (
                len(args) == 1
                and hasattr(args[0], "style")
                and args[0].style == "modification"
                and "Modified local files:" in str(args[0])
            ):
                any_call_found = True
                break

        self.assertTrue(
            any_call_found,
            "Expected a call to console.print with a Text object styled as 'modification' containing 'Modified local files:'",
        )


class TestAddSubparserFunction(TestCase):
    """Test case for the add_subparser function."""

    def test_add_subparser(self):
        """Test adding the scan command to a subparser."""
        # Create a mock ArgumentParser
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")

        # Call the function
        add_subparser(subparsers)

        # Parse arguments to verify the parser works
        args = parser.parse_args(["scan", "path/to/ta"])

        # Verify the arguments were added correctly
        self.assertEqual(args.command, "scan")
        self.assertEqual(args.paths, ["path/to/ta"])
        self.assertFalse(args.recursive)
        self.assertFalse(args.summary)
        self.assertFalse(args.details)
        self.assertIsNone(args.baseline)

    def test_handle_scan_command(self):
        """Test the handle_scan_command function."""
        # Create a mock ArgumentParser
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        add_subparser(subparsers)

        # Parse arguments
        args = parser.parse_args(["scan", "path/to/ta", "--recursive"])

        # Mock scan_command
        with patch("bydefault.commands.scan.scan_command") as mock_scan:
            mock_scan.return_value = 0

            # Call the function
            handle_scan_command(args)

            # Verify scan_command was called with the right arguments
            mock_scan.assert_called_once_with(
                paths=args.paths,
                baseline=args.baseline,
                recursive=args.recursive,
                summary=args.summary,
                details=args.details or not args.summary,
            )
