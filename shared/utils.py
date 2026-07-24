"""
AIStudio Shared Utilities

Generic helper functions used throughout AIStudio.

This module contains only reusable utilities and must never contain
business logic, AI logic or project orchestration.

Author : AIStudio
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path


# ==========================================================
# Time Utilities
# ==========================================================


def utc_now() -> datetime:
    """
    Return the current UTC datetime.
    """

    return datetime.now(UTC)


def timestamp() -> str:
    """
    Return a filesystem-safe timestamp.

    Example
    -------
    20260723_153015
    """

    return utc_now().strftime("%Y%m%d_%H%M%S")


# ==========================================================
# Identifier Utilities
# ==========================================================


def generate_id() -> str:
    """
    Generate a UUID4 string.
    """

    return str(uuid.uuid4())


def generate_project_id() -> str:
    """
    Generate a unique project identifier.
    """

    return f"{timestamp()}_{uuid.uuid4().hex[:8]}"


# ==========================================================
# File Utilities
# ==========================================================


def ensure_directory(
    directory: Path,
) -> Path:
    """
    Ensure a directory exists.
    """

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def safe_filename(
    text: str,
) -> str:
    """
    Convert arbitrary text into a filesystem-safe filename.
    """

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    text = re.sub(
        r"_+",
        "_",
        text,
    )

    return text.strip("_")


def unique_filename(
    name: str,
    extension: str,
) -> str:
    """
    Generate a unique filename.

    Example
    -------
    lion_documentary_4d71bcb4.png
    """

    extension = extension.lstrip(".")

    return (
        f"{safe_filename(name)}_"
        f"{uuid.uuid4().hex[:8]}.{extension}"
    )


# ==========================================================
# Path Utilities
# ==========================================================


def relative_path(
    path: Path,
    root: Path,
) -> str:
    """
    Return a relative path if possible.
    """

    try:

        return str(
            path.relative_to(root)
        )

    except ValueError:

        return str(path)