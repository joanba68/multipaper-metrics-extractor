"""
Logging configuration for metrics-extractor.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for metrics-extractor.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to

    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    l = logging.getLogger("metrics_extractor")

    # Clear any existing handlers
    if l.hasHandlers():
        l.handlers.clear()

    # Set level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")
    l.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    l.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        l.addHandler(file_handler)

    # Don't propagate to the root logger to avoid duplicate logs
    l.propagate = False

    return l


# Create default logger instance
logger = setup_logging()
