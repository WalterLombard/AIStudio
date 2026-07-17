from datetime import datetime
from pathlib import Path
import json
import uuid

from shared.models import ProjectState


def generate_project_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short = str(uuid.uuid4())[:8]
    return f"{timestamp}_{short}"


def create_project_directory(root: Path, project_id: str) -> Path:

    project_path = root / project_id

    folders = [
        "audio",
        "images",
        "video",
        "subtitles",
        "thumbnail",
        "cache",
        "logs",
        "exports"
    ]

    project_path.mkdir(parents=True, exist_ok=True)

    for folder in folders:
        (project_path / folder).mkdir(exist_ok=True)

    return project_path


def save_project_state(project: ProjectState, path: Path):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            project.model_dump(mode="json"),
            f,
            indent=4,
            ensure_ascii=False
        )