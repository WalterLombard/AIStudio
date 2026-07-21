"""
AIStudio Motion Designer Agent

Generates the cinematic motion plan one image at a time.

Each generated image receives its own camera movement which keeps
prompts small, avoids LLM timeouts and allows individual regeneration.

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

    def _generate_scene(
        self,
        storyboard_scene: dict,
        image_asset: dict,
    ) -> MotionSceneResponse:
        """
        Generate one camera move.
        """

        prompt = json.dumps(

            {

                "storyboard_scene": storyboard_scene,

                "image_asset": image_asset,

            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating motion for %s",

            image_asset["asset_id"],

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

        if state.storyboard is None:

            raise ValueError(
                "StoryboardData must exist before MotionDesignerAgent runs."
            )

        motion = MotionData()

        image_assets = [

            asset

            for asset in self.assets.get_assets_by_type(
                "image"
            )

        ]

        for storyboard_scene, image_asset in zip(

            state.storyboard.scenes,

            image_assets,

            strict=False,

        ):

            response = self._generate_scene(

                storyboard_scene.model_dump(),

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