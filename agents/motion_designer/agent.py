"""
AIStudio Motion Designer Agent

Generates the cinematic motion plan one shot at a time.

Each approved Shot Specification receives its own camera movement.
This keeps prompts small, avoids LLM timeouts and allows individual
shots to be regenerated independently.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    MotionData,
    MotionSceneResponse,
    ProjectState,
)

from shared.services import (
    AssetService,
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("MotionDesignerAgent")


class MotionDesignerAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_motion(
        self,
        shot: dict,
        image_asset: dict,
    ) -> MotionSceneResponse:
        """
        Generate motion for one approved shot.
        """

        prompt = json.dumps(

            {

                "shot": shot,

                "image_asset": image_asset,

            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating motion for shot %s",

            shot["shot_number"],

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return MotionSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.shots is None:

            raise ValueError(
                "ShotData must exist before MotionDesignerAgent runs."
            )

        motion = MotionData()

        image_assets = [

            asset

            for asset in self.assets.get_assets_by_type(
                "image"
            )

        ]

        for shot, image_asset in zip(

            state.shots.shots,

            image_assets,

            strict=False,

        ):

            response = self._generate_motion(

                shot.model_dump(),

                image_asset.model_dump(),

            )

            motion.scenes.append(
                response.scene
            )

        motion.total_duration = sum(

            scene.duration

            for scene in motion.scenes

        )

        state.motion = motion

        state.current_stage = "motion"

        state.status = "motion_complete"

        LOGGER.info(
            "Motion Designer Agent completed successfully."
        )

        return state