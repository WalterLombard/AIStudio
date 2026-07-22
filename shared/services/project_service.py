"""
AIStudio Project Service

Responsible for creating and managing AIStudio projects.

Author : AIStudio
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProjectService:
    """
    Manages AIStudio project folders and project files.
    """

    def __init__(self) -> None:
        self.root = Path("projects")
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create(
        self,
        project_name: str,
    ) -> Path:
        """
        Create a new AIStudio project structure.
        """
        project = self.root / project_name
        project.mkdir(
            parents=True,
            exist_ok=True,
        )

        folders = [
            "research",
            "script",
            "storyboard",
            "visuals",
            "audio",
            "video",
            "exports",
            "cache",
        ]

        for folder in folders:
            (project / folder).mkdir(
                exist_ok=True,
            )

        return project

    def save_json(
        self,
        project: Path,
        relative_path: str,
        data: Any,
    ) -> None:
        """
        Save JSON data into the project folder.
        """
        file = project / relative_path
        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False,
            )

    def load_json(
        self,
        project: Path,
        relative_path: str,
    ) -> Any:
        """
        Load JSON data from the project folder.
        """
        file = project / relative_path

        if not file.exists():
            raise FileNotFoundError(f"Project asset not found: {file}")

        with open(
            file,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)