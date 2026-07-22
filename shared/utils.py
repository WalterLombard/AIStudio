"""
AIStudio Shared Utilities

Common helper functions used throughout AIStudio.

This module contains only generic reusable utilities.
It must never contain agent-specific logic.

Author : AIStudio
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from shared.models import ProjectState


# ==========================================================
# Time Utilities
# ==========================================================

def timestamp() -> str:
    """Returns the current timestamp in YYYYMMDD_HHMMSS format."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ==========================================================
# Project Utilities
# ==========================================================

def generate_project_id() -> str:
    """Generates a unique project identifier."""
    short_id = str(uuid.uuid4())[:8]
    return f"{timestamp()}_{short_id}"


def create_project_directory(
    root: Path | str,
    project_id: str,
) -> Path:
    """Creates the directory structure for a project."""
    root_path = Path(root)
    project_path = root_path / project_id

    directories = [
        "audio",
        "images",
        "video",
        "subtitles",
        "thumbnail",
        "cache",
        "logs",
        "exports",
    ]

    project_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    for directory in directories:
        (project_path / directory).mkdir(exist_ok=True)

    return project_path


# ==========================================================
# JSON Utilities
# ==========================================================

def save_project_state(
    project: ProjectState,
    filename: Path | str,
) -> None:
    """Saves a ProjectState instance to a JSON file."""
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            project.model_dump(mode="json"),
            file,
            indent=4,
            ensure_ascii=False,
        )


def load_project_state(filename: Path | str) -> ProjectState:
    """Loads a ProjectState instance from a JSON file."""
    file_path = Path(filename)

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ProjectState(**data)


# ==========================================================
# File Utilities
# ==========================================================

def safe_filename(text: str) -> str:
    """Converts raw text into a filesystem-safe string."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")