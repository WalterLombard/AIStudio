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
    Generates publishing metadata and packages exports using compact state memory.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before packaging.
        """
        if getattr(state, "final_video_path", None) is None and (getattr(state, "video", None) is None or not getattr(state.video, "filename", None)):
            raise ValueError(
                "PublisherAgent failure: final_video_path or valid video asset must exist before PublisherAgent runs."
            )

    def run(self, state: ProjectState) -> ProjectState:
        """
        Executes the publisher packaging step using memory integration and context payloads.
        """
        self._validate_state(state)

        LOGGER.info("Starting Publisher Agent")

        project_id = getattr(state, "project_id", "project_01")
        title = getattr(state, "title", None)
        if not title and state.production_brief:
            title = getattr(state.production_brief, "title", "Untitled")
        elif not title:
            title = "Untitled"

        production_brief = state.production_brief.model_dump() if state.production_brief else None

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        # Extract script text cleanly if available
        script_text = getattr(state, "script_text", "")
        if not script_text and getattr(state, "script", None) and hasattr(state.script, "scenes"):
            script_text = " ".join([scene.narration for scene in state.script.scenes if hasattr(scene, "narration")])

        video_path = str(getattr(state, "final_video_path", None) or (state.video.filename if state.video else ""))
        subtitle_path = str(getattr(state, "subtitle_file_path", ""))

        export_summary = None

        try:
            if generate_metadata_and_package and hasattr(generate_metadata_and_package, "generate_with_context"):
                export_summary = generate_metadata_and_package(
                    project_id=project_id,
                    title=title,
                    production_brief=production_brief,
                    script_text=script_text,
                    video_path=video_path,
                    subtitle_path=subtitle_path,
                )
            elif generate_metadata_and_package:
                export_summary = generate_metadata_and_package(
                    project_id=project_id,
                    title=title,
                    script_text=script_text,
                    video_path=video_path,
                    subtitle_path=subtitle_path,
                )
            else:
                LOGGER.info("Publisher server unavailable. Falling back to native LLM metadata generation.")
                prompt_payload = {
                    "project_id": project_id,
                    "title": title,
                    "outline_summary": outline_summary,
                    "script_summary": script_text[:1500],  # Keep prompt size concise
                    "video_path": video_path,
                    "subtitle_path": subtitle_path,
                }
                if production_brief:
                    prompt_payload["production_brief"] = {
                        "title": production_brief.get("title"),
                        "topic": production_brief.get("topic"),
                        "tone": production_brief.get("tone"),
                        "target_audience": production_brief.get("target_audience"),
                        "tags": production_brief.get("tags", []),
                    }

                prompt = json.dumps(prompt_payload, indent=4, ensure_ascii=False)

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