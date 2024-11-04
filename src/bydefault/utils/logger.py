"""Logging utilities for byDefault."""

import logging


def setup_logger() -> logging.Logger:
    """Set up and return a configured logger."""
    logger = logging.getLogger("bydefault")
    # TODO: Configure logger
    return logger
