"""
AIStudio Project Service

Responsible for creating, loading, saving and managing AIStudio
projects throughout the production pipeline.

Author : AIStudio
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared.logger import get_logger
from shared.models import ProjectState


LOGGER = get_logger("ProjectService")


class ProjectService:
    """
    Central project management service.
    """

    PROJECT_ROOT = Path("projects")

    PROJECT_FOLDERS = [
        "assets",
        "cache",
        "exports",
        "logs",
        "prompts",
        "research",
        "script",
        "storyboard",
        "visuals",
        "images",
        "motion",
        "audio",
        "video",
        "registry",
        "temp",
    ]

    STATE_FILENAME = "project_state.json"

    def __init__(self) -> None:

        self.PROJECT_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        LOGGER.info(
            "ProjectService initialized."
        )

    def create(
        self,
        project_name: str,
    ) -> Path:
        """
        Create a new AIStudio project.
        """

        project = self.PROJECT_ROOT / project_name

        project.mkdir(
            parents=True,
            exist_ok=True,
        )

        for folder in self.PROJECT_FOLDERS:

            (
                project / folder
            ).mkdir(
                parents=True,
                exist_ok=True,
            )

        LOGGER.info(
            "Created project '%s'.",
            project_name,
        )

        return project

    def save_state(
        self,
        project: Path,
        state: ProjectState,
    ) -> None:
        """
        Persist the complete ProjectState.
        """

        filename = project / self.STATE_FILENAME

        filename.write_text(

            state.model_dump_json(
                indent=4,
            ),

            encoding="utf-8",

        )

        LOGGER.info(
            "Saved ProjectState."
        )

    def load_state(
        self,
        project: Path,
    ) -> ProjectState:
        """
        Load a ProjectState from disk.
        """

        filename = project / self.STATE_FILENAME

        LOGGER.info(
            "Loading ProjectState."
        )

        return ProjectState.model_validate_json(

            filename.read_text(
                encoding="utf-8",
            )

        )

    def save_json(
        self,
        project: Path,
        relative_path: str,
        data: Any,
    ) -> None:
        """
        Save arbitrary JSON into the project.
        """

        filename = project / relative_path

        filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename.write_text(

            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),

            encoding="utf-8",

        )

        LOGGER.info(
            "Saved %s",
            filename,
        )

    def load_json(
        self,
        project: Path,
        relative_path: str,
    ) -> Any:
        """
        Load arbitrary JSON from the project.
        """

        filename = project / relative_path

        LOGGER.info(
            "Loaded %s",
            filename,
        )

        return json.loads(

            filename.read_text(
                encoding="utf-8",
            )

        )

    def exists(
        self,
        project_name: str,
    ) -> bool:
        """
        Determine whether a project exists.
        """

        return (
            self.PROJECT_ROOT / project_name
        ).exists()

    def list_projects(
        self,
    ) -> list[str]:
        """
        Return all available AIStudio projects.
        """

        return sorted(

            project.name

            for project in self.PROJECT_ROOT.iterdir()

            if project.is_dir()

        )

    def delete(
        self,
        project_name: str,
    ) -> None:
        """
        Delete a project directory.

        This intentionally raises NotImplementedError until a safe
        deletion strategy (confirmation, archive, recycle bin, etc.)
        is implemented.
        """

        raise NotImplementedError(
            "Project deletion has not yet been implemented."
        )