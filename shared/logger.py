"""
AIStudio Shared Logger

This module provides the single logging implementation used throughout
the AIStudio project.

Every component obtains its logger from this module.

Author : AIStudio
"""

from __future__ import annotations

import logging
from pathlib import Path


class Logger:
    """
    Central logging service for AIStudio.
    """

    LOG_DIRECTORY = Path("logs")

    @classmethod
    def get_logger(
        cls,
        name: str,
    ) -> logging.Logger:
        """
        Returns a configured logger.
        """

        cls.LOG_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger = logging.getLogger(name)

        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        log_file = cls.LOG_DIRECTORY / f"{name}.log"

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        logger.addHandler(console_handler)

        logger.propagate = False

        return logger


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Convenience function used throughout AIStudio.

    Example
    -------
    logger = get_logger("ExecutiveProducer")
    """

    return Logger.get_logger(name)