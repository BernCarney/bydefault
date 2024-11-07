"""Tests for logger utility functions."""

import logging

import pytest

from bydefault.utils.logger import setup_logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger between tests."""
    # We should also reset the global instance
    import bydefault.utils.logger as logger_module

    logger_module._logger_instance = None

    logger = logging.getLogger("bydefault")
    logger.handlers = []
    logger.setLevel(logging.NOTSET)
    yield


@pytest.fixture(autouse=True)
def configure_caplog(caplog):
    """Configure caplog for all tests."""
    # Ensure caplog captures at all levels
    caplog.set_level(logging.DEBUG)
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
    # Configure caplog to capture all levels
    caplog.set_level(logging.DEBUG)

    logger = setup_logger()
    logger.propagate = True  # Ensure messages propagate to root logger

    # Test messages at different levels
    test_message = "Test message"
    error_message = "Error message"

    logger.info(test_message)
    logger.error(error_message)

    # Check the messages in caplog
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == test_message
    assert caplog.records[1].levelname == "ERROR"
    assert caplog.records[1].message == error_message


def test_logger_levels(caplog):
    """Test logger at different levels."""
    # Configure caplog to capture all levels
    caplog.set_level(logging.DEBUG)

    logger = setup_logger(log_level=logging.DEBUG)
    logger.propagate = True  # Ensure messages propagate to root logger

    messages = {
        "debug": "Debug message",
        "info": "Info message",
        "warning": "Warning message",
        "error": "Error message",
    }

    # Log messages at different levels
    logger.debug(messages["debug"])
    logger.info(messages["info"])
    logger.warning(messages["warning"])
    logger.error(messages["error"])

    # Verify all messages were captured
    assert len(caplog.records) == 4

    # Verify each message and its level
    expected_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
    for record, level in zip(caplog.records, expected_levels, strict=True):
        assert record.levelno == level


def test_logger_singleton_config():
    """Test logger maintains configuration across instances."""
    logger1 = setup_logger()
    original_level = logger1.level

    # Change level
    logger1.setLevel(logging.DEBUG)

    # Get another instance
    logger2 = setup_logger()
    assert logger2.level == logging.DEBUG

    # Reset for other tests
    logger1.setLevel(original_level)


def test_setup_logger_with_custom_level() -> None:
    """Test logger setup with custom log level."""
    logger = setup_logger(log_level=logging.DEBUG)

    # Test logger instance and level
    assert logger.level == logging.DEBUG
    assert logger.handlers[0].level == logging.DEBUG


def test_logger_singleton_respects_initial_level():
    """Test that singleton logger respects the initial log level setting."""
    # First setup with DEBUG
    logger1 = setup_logger(log_level=logging.DEBUG)
    assert logger1.level == logging.DEBUG

    # Second setup with different level - should return same instance with DEBUG
    logger2 = setup_logger(log_level=logging.ERROR)
    assert logger2.level == logging.DEBUG  # Still DEBUG from first setup
    assert logger1 is logger2  # Same instance
