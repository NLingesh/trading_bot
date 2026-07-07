"""
Centralized logging configuration for the trading bot.

Logs are written both to the console (INFO and above) and to a rotating
log file at `logs/bot.log` (DEBUG and above), capturing full request /
response details, errors, and warnings.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

_LOGGER_NAME = "trading_bot"
_CONFIGURED = False


def setup_logging(log_level: str = "DEBUG") -> logging.Logger:
    """
    Configure and return the shared trading bot logger.

    This function is idempotent: calling it multiple times will not
    attach duplicate handlers.

    Args:
        log_level: Minimum log level for the file handler (e.g. "DEBUG", "INFO").

    Returns:
        The configured `logging.Logger` instance.
    """
    global _CONFIGURED

    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)

    if _CONFIGURED:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: 5 MB per file, keep 5 backups.
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
    file_handler.setFormatter(formatter)

    # Console handler: INFO and above, for readable operator feedback.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _CONFIGURED = True
    return logger


def get_logger() -> logging.Logger:
    """Return the shared trading bot logger, configuring it if necessary."""
    if not _CONFIGURED:
        return setup_logging()
    return logging.getLogger(_LOGGER_NAME)
