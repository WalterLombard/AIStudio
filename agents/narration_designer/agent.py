"""
AIStudio Narration Designer Agent

Generates the narration performance one shot at a time.

Each approved Shot Specification receives its own narration
performance instructions. This keeps prompts small, avoids LLM
timeouts and allows individual shots to be regenerated.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    NarrationData,
    NarrationSceneResponse,
    ProjectState,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("NarrationDesignerAgent")


class NarrationDesignerAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_segment(
        self,
        shot: dict,
        motion_scene: dict,
    ) -> NarrationSceneResponse:
        """
        Generate narration performance for one shot.
        """

        prompt = json.dumps(

            {

                "shot": shot,

                "motion": motion_scene,

            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating narration for shot %s",

            shot["shot_number"],

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return NarrationSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.shots is None:

            raise ValueError(
                "ShotData must exist before NarrationDesignerAgent runs."
            )

        if state.motion is None:

            raise ValueError(
                "MotionData must exist before NarrationDesignerAgent runs."
            )

        narration = NarrationData()

        for shot, motion_scene in zip(

            state.shots.shots,

            state.motion.scenes,

            strict=False,

        ):

            response = self._generate_segment(

                shot.model_dump(),

                motion_scene.model_dump(),

            )

            narration.segments.append(
                response.segment
            )

        state.narration = narration

        state.current_stage = "narration"

        state.status = "narration_complete"

        LOGGER.info(
            "Narration Designer Agent completed successfully."
        )

        return state