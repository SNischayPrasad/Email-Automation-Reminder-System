"""
logger.py
---------
Sets up logging so every action is written to:
  * the terminal (so you see progress live)
  * logs/app.log (full history)
  * logs/sent.log and logs/failed.log (quick view of results)
"""

import logging
import sys

from src import config

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _file_handler(filename: str, level=logging.INFO) -> logging.FileHandler:
    handler = logging.FileHandler(config.LOGS_DIR / filename, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    return handler


def get_logger() -> logging.Logger:
    """Main application logger (terminal + logs/app.log)."""
    config.ensure_folders()
    logger = logging.getLogger("email_automation")
    if logger.handlers:          # already configured - don't add twice
        return logger

    logger.setLevel(logging.INFO)
    console = logging.StreamHandler(sys.stdout)  # stdout keeps order with print()
    console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S"))
    logger.addHandler(console)
    logger.addHandler(_file_handler("app.log"))
    return logger


def get_result_logger(name: str) -> logging.Logger:
    """Separate loggers for sent.log and failed.log (file only)."""
    config.ensure_folders()
    logger = logging.getLogger(f"email_automation.{name}")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(_file_handler(f"{name}.log"))
        logger.propagate = False  # don't duplicate into app.log/terminal
    return logger
