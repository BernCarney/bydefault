"""Shared test fixtures and configuration."""

import pytest
from click.testing import CliRunner
from rich.console import Console


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_console(mocker):
    """Create a mocked Rich console."""
    console = mocker.create_autospec(Console)
    return console
