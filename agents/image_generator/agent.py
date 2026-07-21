"""
AIStudio Image Generator Agent

Generates one image at a time from the Shot Plan.

Each shot is processed independently which keeps prompts
small, allows retries and avoids losing progress.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    ImageData,
    ImageSceneResponse,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("ImageGeneratorAgent")


class ImageGeneratorAgent:
    """
    Generates one image for every planned shot.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_image(
        self,
        production_brief: dict,
        shot: dict,
    ) -> ImageSceneResponse:
        """
        Generate one image prompt.
        """

        prompt = json.dumps(

            {
                "production_brief": production_brief,
                "shot": shot,
            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating image for scene %s shot %s",

            shot.get(
                "scene_id",
                "?",
            ),

            shot.get(
                "shot_number",
                "?",
            ),

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.15,

        )

        return ImageSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief must exist before ImageGeneratorAgent runs."
            )

        if state.shots is None:

            raise ValueError(
                "ShotData must exist before ImageGeneratorAgent runs."
            )

        LOGGER.info(
            "Starting Image Generator Agent"
        )

        production_brief = (
            state.production_brief.model_dump()
        )

        images = ImageData()

        #
        # Generate one image per shot
        #

        for shot in state.shots.shots:

            response = self._generate_image(

                production_brief=production_brief,

                shot=shot.model_dump(),

            )

            images.images.append(
                response.image
            )

        state.images = images

        state.current_stage = "images"

        state.status = "images_complete"

        LOGGER.info(
            "Image Generator Agent completed successfully."
        )

        return state