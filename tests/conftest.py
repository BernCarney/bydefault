"""Shared test fixtures and configuration."""

import os
import subprocess

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture(scope="session", autouse=False)
def ensure_test_environment():
    """Ensure the test_tas directory exists for testing.

    This fixture checks if the test_tas directory exists and runs the
    create_test_tas.sh script if it doesn't. It's not run automatically
    but can be included in tests that need the test environment.
    """
    if not os.path.exists("test_tas"):
        print("Test TA environment not found. Creating it...")
        try:
            # Use "yes n" to avoid overwriting if it exists but wasn't detected
            subprocess.run(
                "yes n | ./scripts/create_test_tas.sh", shell=True, check=True
            )
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Failed to create test TA environment: {e}")

    # Verify that at least some expected test TAs exist
    for ta in ["TA_valid", "TA_invalid"]:
        if not os.path.exists(f"test_tas/{ta}"):
            pytest.fail(f"Test TA environment missing expected directory: {ta}")
