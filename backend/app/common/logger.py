"""
Logger configuration module.

This module provides a reusable logger instance for the application
and a simple helper function for conditional logging based on a global setting.
"""

import logging
from sys import stdout
from time import gmtime

from app.common.settings import settings


def get_logger() -> logging.Logger:
    """
    Returns a configured singleton logger for the application.

    The logger is configured to:
    - Output to stdout
    - Format messages with timestamps, log levels, and logger names
    - Use UTC time (via gmtime)

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger("app")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    formatter.converter = gmtime

    handler = logging.StreamHandler(stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


def log(msg: str, force: bool = False) -> None:
    """
    Logs a message using the application logger.

    The message will only be logged if `settings.FULL_LOGS` is True,
    unless `force=True` is explicitly provided.

    Args:
        msg (str): The message to log.
        force (bool): If True, forces logging regardless of settings.
    """
    if settings.FULL_LOGS or force:
        get_logger().info(f"{msg}")
