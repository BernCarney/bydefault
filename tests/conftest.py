"""Shared test fixtures and configuration."""

from pathlib import Path
from typing import Generator

import pytest
from click.testing import CliRunner


def pytest_configure(config):
    """Configure pytest for our project."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test",
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_ta_dir(test_data_dir: Path) -> Generator[Path, None, None]:
    """Create and return path to a sample TA directory."""
    ta_dir = test_data_dir / "TA-test"
    ta_dir.mkdir(parents=True, exist_ok=True)
    (ta_dir / "local").mkdir(exist_ok=True)
    (ta_dir / "default").mkdir(exist_ok=True)
    (ta_dir / "metadata").mkdir(exist_ok=True)

    yield ta_dir

    # Cleanup
    if ta_dir.exists():
        import shutil

        shutil.rmtree(ta_dir)
