"""
AIStudio Narration Designer Agent

Generates the narration performance one scene at a time.

Each script scene is converted independently which keeps prompts
small, avoids LLM timeouts and allows regeneration of individual
segments.

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

    def _generate_scene(
        self,
        script_scene: dict,
        motion_scene: dict,
    ) -> NarrationSceneResponse:
        """
        Generate one narration segment.
        """

        prompt = json.dumps(

            {

                "script_scene": script_scene,

                "motion_scene": motion_scene,

            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating narration for scene %s",

            script_scene["scene"],

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

        if state.script is None:

            raise ValueError(
                "ProjectState does not contain ScriptData."
            )

        if state.motion is None:

            raise ValueError(
                "ProjectState does not contain MotionData."
            )

        narration = NarrationData()

        for script_scene, motion_scene in zip(

            state.script.scenes,

            state.motion.scenes,

            strict=False,

        ):

            response = self._generate_scene(

                script_scene.model_dump(),

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