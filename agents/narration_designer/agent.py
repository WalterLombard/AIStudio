"""
AIStudio Narration Designer Agent

Creates the narration performance plan from the documentary script.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    NarrationData,
    ProjectState,
)

from shared.services import (
    LLMService,
    PromptService,
)


class NarrationDesignerAgent:
    """
    Produces the narration performance plan.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

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

        prompt = json.dumps(

            {

                "script":
                    state.script.model_dump(),

                "motion":
                    state.motion.model_dump(),

            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        state.narration = NarrationData(
            **result
        )

        state.current_stage = "narration"

        state.status = "narration_complete"

        return state