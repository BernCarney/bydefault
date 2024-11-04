"""Tests for logger utility functions."""

import logging

import pytest

from bydefault.utils.logger import setup_logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger between tests."""
    logger = logging.getLogger("bydefault")
    logger.handlers = []
    logger.setLevel(logging.NOTSET)
    yield


def test_setup_logger() -> None:
    """Test logger setup and configuration."""
    logger = setup_logger()

    # Test logger instance
    assert isinstance(logger, logging.Logger)
    assert logger.name == "bydefault"

    # Test log level
    assert logger.level == logging.INFO

    # Test handler configuration
    assert len(logger.handlers) > 0
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)


def test_logger_singleton() -> None:
    """Test that multiple calls return the same logger."""
    logger1 = setup_logger()
    logger2 = setup_logger()
    assert logger1 is logger2


def test_logger_messages(caplog) -> None:
    """Test logger message formatting."""
    logger = setup_logger()

    with caplog.at_level(logging.INFO):
        logger.info("Test message")
        assert "Test message" in caplog.text

        logger.error("Error message")
        assert "Error message" in caplog.text
