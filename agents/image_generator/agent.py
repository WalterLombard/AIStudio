"""
AIStudio Image Generator Agent

Generates one image at a time from the Shot Plan using LLM
or FastMCP image server specifications.
Optionally passes visual assets to asset_server for processing/upscaling.

Each shot is processed independently which keeps prompts
small, allows retries and avoids losing progress.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from shared.models import (
    ImageData,
    ImageSceneResponse,
    ProjectState,
)
from shared.services import (
    LLMService,
    PromptService,
)

# Optional import of FastMCP image server module
try:
    from servers.image_server import generate_image_specification
except ImportError:
    generate_image_specification = None

# Optional import of asset_server FastMCP tool
try:
    from servers.asset_server import process_and_upscale_asset
except ImportError:
    process_and_upscale_asset = None

LOGGER = logging.getLogger("ImageGeneratorAgent")


class ImageGeneratorAgent:
    """
    Generates one image specification/prompt for every planned shot using compact state memory.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.production_brief is None:
            raise ValueError(
                "ImageGeneratorAgent failure: ProductionBrief must exist before ImageGeneratorAgent runs."
            )
        if state.shots is None or not state.shots.shots:
            raise ValueError(
                "ImageGeneratorAgent failure: ShotData must exist before ImageGeneratorAgent runs."
            )

    def _generate_image(
        self,
        production_brief: dict,
        shot: dict,
        last_image_spec: dict | None,
        outline_summary: list[dict],
    ) -> ImageSceneResponse:
        """
        Generate one image prompt using compact context payloads.
        """
        scene_id = shot.get("scene_id", "?")
        shot_num = shot.get("shot_number", "?")

        LOGGER.info("Generating image for scene %s shot %s", scene_id, shot_num)

        try:
            if generate_image_specification:
                result = generate_image_specification(
                    production_brief=production_brief,
                    shot=shot,
                    completed_images=[last_image_spec] if last_image_spec else [],
                )
            else:
                prompt = json.dumps(
                    {
                        "production_brief": {
                            "title": production_brief.get("title"),
                            "topic": production_brief.get("topic"),
                            "tone": production_brief.get("tone"),
                            "story_arc": production_brief.get("story_arc"),
                        },
                        "outline_summary": outline_summary,
                        "shot": shot,
                        "previous_image_spec": last_image_spec,
                    },
                    indent=4,
                    ensure_ascii=False,
                )
                result = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=prompt,
                    temperature=0.15,
                )
        except Exception as err:
            raise RuntimeError(
                f"ImageGeneratorAgent failure during generation for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

        try:
            if isinstance(result, ImageSceneResponse):
                return result

            # Flexible parsing: Handles {"image": {...}} and direct {...} outputs
            if isinstance(result, dict):
                if "image" in result and isinstance(result["image"], dict) and "image" in result["image"]:
                    return ImageSceneResponse(**result)
                elif "image" in result and isinstance(result["image"], dict):
                    return ImageSceneResponse(image=result["image"])
                else:
                    return ImageSceneResponse(image=result)
            else:
                return ImageSceneResponse(image=result)
        except Exception as err:
            raise ValueError(
                f"ImageGeneratorAgent failed to validate output for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the image generation pipeline step using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Image Generator Agent")

        production_brief = state.production_brief.model_dump()
        images = ImageData()

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        last_image_spec: dict | None = None

        # Generate one image prompt per shot
        for shot in state.shots.shots:
            shot_dict = shot.model_dump()
            scene_id = shot_dict.get("scene_id", "?")
            shot_num = shot_dict.get("shot_number", "?")

            response = self._generate_image(
                production_brief=production_brief,
                shot=shot_dict,
                last_image_spec=last_image_spec,
                outline_summary=outline_summary,
            )

            img_obj = response.image
            last_image_spec = img_obj.model_dump() if hasattr(img_obj, "model_dump") else img_obj

            # Post-process or upscale via asset_server if file_path exists on image model
            file_path = getattr(img_obj, "file_path", None) or getattr(img_obj, "path", None)
            if file_path and process_and_upscale_asset and Path(str(file_path)).exists():
                LOGGER.info("Processing visual asset via asset_server for Scene %s Shot %s", scene_id, shot_num)
                processed_path = process_and_upscale_asset(
                    input_path=str(file_path),
                    target_resolution=(1920, 1080),
                )
                if hasattr(img_obj, "file_path"):
                    img_obj.file_path = processed_path
                elif hasattr(img_obj, "path"):
                    img_obj.path = processed_path

            images.images.append(img_obj)

        state.images = images
        state.current_stage = "images"
        state.status = "images_complete"

        LOGGER.info("Image Generator Agent completed successfully.")

        return state