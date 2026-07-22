"""
AIStudio Publisher Agent

Packages final render outputs, generates platform SEO metadata,
and formats description blocks using LLM or FastMCP publisher server.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import ProjectState
from shared.services import (
    LLMService,
    PromptService,
)

# Optional import of FastMCP publisher server module
try:
    from servers.publisher_server import generate_metadata_and_package
except ImportError:
    generate_metadata_and_package = None

LOGGER = logging.getLogger("PublisherAgent")


class PublisherAgent:
    """
    Generates publishing metadata and packages exports.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before packaging.
        """
        if getattr(state, "final_video_path", None) is None:
            raise ValueError(
                "PublisherAgent failure: final_video_path must exist before PublisherAgent runs."
            )

    def run(self, state: ProjectState) -> ProjectState:
        """
        Executes the publisher packaging step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Publisher Agent")

        project_id = getattr(state, "project_id", "project_01")
        title = getattr(state, "title", state.production_brief.title if getattr(state, "production_brief", None) else "Untitled")
        
        # Extract script text cleanly if available
        script_text = getattr(state, "script_text", "")
        if not script_text and getattr(state, "script", None):
            script_text = " ".join([scene.narration for scene in getattr(state.script, "scenes", []) if hasattr(scene, "narration")])

        video_path = str(state.final_video_path)
        subtitle_path = str(getattr(state, "subtitle_file_path", ""))

        export_summary = None

        try:
            if generate_metadata_and_package:
                export_summary = generate_metadata_and_package(
                    project_id=project_id,
                    title=title,
                    script_text=script_text,
                    video_path=video_path,
                    subtitle_path=subtitle_path,
                )
            else:
                LOGGER.info("Publisher server unavailable. Falling back to native LLM metadata generation.")
                prompt_data = {
                    "project_id": project_id,
                    "title": title,
                    "script_summary": script_text[:1500], # Keep prompt size concise
                    "video_path": video_path,
                    "subtitle_path": subtitle_path,
                }
                prompt = json.dumps(prompt_data, indent=4, ensure_ascii=False)
                
                export_summary = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=prompt,
                    temperature=0.3,
                )
        except Exception as err:
            raise RuntimeError(
                f"PublisherAgent failed during metadata generation and packaging: {err}"
            ) from err

        state.export_summary = export_summary
        state.current_stage = "publisher"
        state.status = "publisher_complete"

        LOGGER.info("Publisher Agent completed successfully.")

        return state