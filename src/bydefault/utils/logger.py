"""Logging utilities for byDefault."""

import logging
import sys
from typing import Optional

_logger_instance: Optional[logging.Logger] = None


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """Set up and return a logger instance.

    Args:
        log_level: The logging level to use. Defaults to logging.INFO.
                  Can be logging.DEBUG, logging.INFO, logging.WARNING,
                  logging.ERROR, or logging.CRITICAL.

    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance

    # Create logger
    logger = logging.getLogger("bydefault")
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Configure logger with provided log level
    logger.setLevel(log_level)
    logger.propagate = False
    
    # Add handler with matching log level
    handler = logging.StreamHandler(sys.stderr)  # Use stderr for consistency with pytest
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _logger_instance = logger
    return logger
