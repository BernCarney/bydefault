"""Logging utilities for byDefault."""

import logging


def setup_logger() -> logging.Logger:
    """Set up and return a configured logger."""
    logger = logging.getLogger("bydefault")
    logger.setLevel(logging.INFO)

    # Add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
