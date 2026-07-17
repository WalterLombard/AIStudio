from pathlib import Path
from datetime import datetime
import json
import re

from shared.models import ProjectState, ProjectMetadata


class ProjectManager:

    def __init__(self, root: str = "projects"):

        self.root = Path(root)

        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_name(self, text: str) -> str:

        text = text.lower()

        text = re.sub(r"[^a-z0-9]+", "_", text)

        return text.strip("_")

    def create_project(
        self,
        title: str,
        topic: str,
        audience: str,
        duration_seconds: int = 300,
        language: str = "English",
    ) -> ProjectState:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        folder_name = f"{timestamp}_{self._safe_name(title)}"

        project_folder = self.root / folder_name

        project_folder.mkdir()

        folders = [

            "research",

            "storyboard",

            "script",

            "prompts",

            "images",

            "video",

            "audio",

            "exports",

            "logs",

            "temp"

        ]

        for folder in folders:

            (project_folder / folder).mkdir()

        metadata = ProjectMetadata(

            title=title,

            topic=topic,

            audience=audience,

            duration_seconds=duration_seconds,

            language=language,

        )

        project = ProjectState(

            project_id=folder_name,

            metadata=metadata,

        )

        with open(project_folder / "project.json", "w", encoding="utf-8") as file:

            json.dump(

                project.model_dump(mode="json"),

                file,

                indent=4,

                ensure_ascii=False,

            )

        return project