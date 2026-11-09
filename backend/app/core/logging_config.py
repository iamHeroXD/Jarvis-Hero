"""
JARVIS Logging Configuration
Structured logging with file rotation and rich console output.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure application-wide logging.
    Returns the root JARVIS logger.
    """
    logger = logging.getLogger("jarvis")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates on reload
    logger.handlers.clear()

    # ── Rich Console Handler ──────────────────────────────────────────────
    console_handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        show_path=False,
        markup=True,
    )
    console_handler.setFormatter(
        logging.Formatter("%(message)s", datefmt="[%H:%M:%S]")
    )
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.addHandler(console_handler)

    # ── File Handler ─────────────────────────────────────────────────────
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler.setLevel(logging.DEBUG)  # Always full detail in file
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the jarvis namespace."""
    return logging.getLogger(f"jarvis.{name}")
