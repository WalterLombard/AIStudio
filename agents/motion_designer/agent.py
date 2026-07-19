"""
AIStudio Motion Designer Agent

Creates the cinematic motion plan for the documentary.

The Motion Designer analyses the storyboard together with the
generated image assets and determines camera movement, timing,
transitions and pacing.

The output is MotionData.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    MotionData,
    ProjectState,
)

from shared.services import (
    AssetService,
    LLMService,
    PromptService,
)


class MotionDesignerAgent:
    """
    Produces the complete cinematic motion plan.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Build the cinematic motion plan.
        """

        if state.storyboard is None:

            raise ValueError(
                "ProjectState does not contain StoryboardData."
            )

        image_assets = [

            asset.model_dump()

            for asset in self.assets.get_assets_by_type(
                "image"
            )

        ]

        prompt = json.dumps(

            {

                "storyboard":
                    state.storyboard.model_dump(),

                "image_assets":
                    image_assets,

            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        state.motion = MotionData(
            **result
        )

        state.current_stage = "motion"

        state.status = "motion_complete"

        return state