from pathlib import Path

from fastmcp import FastMCP

from shared.config import config
from shared.logger import get_logger
from shared.models import ProjectState
from shared.utils import (
    generate_project_id,
    create_project_directory,
    save_project_state,
)

logger = get_logger("orchestrator")

mcp = FastMCP("Orchestrator")


ROOT = Path(__file__).resolve().parent.parent

PROJECT_ROOT = ROOT / config.get("paths.projects")


PROJECT_ROOT.mkdir(exist_ok=True)


@mcp.tool()

def create_project(topic: str):

    """
    Creates a new AI Studio project.
    """

    logger.info("Creating new project.")

    project_id = generate_project_id()

    project_folder = create_project_directory(
        PROJECT_ROOT,
        project_id
    )

    project = ProjectState(project_id=project_id)

    project.metadata.topic = topic

    save_project_state(
        project,
        project_folder / "project.json"
    )

    logger.info(f"Project {project_id} created.")

    return {

        "project_id": project_id,

        "folder": str(project_folder)

    }


if __name__ == "__main__":
    mcp.run()