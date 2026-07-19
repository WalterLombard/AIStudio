"""
AIStudio Storyboard Agent

Generates a cinematic storyboard from the completed documentary script.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    ProjectState,
    StoryboardData,
)

from shared.services import (
    LLMService,
    PromptService,
)


class StoryboardAgent:
    """
    Produces the cinematic storyboard.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__
        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.production_brief is None:
            raise ValueError(
                "ProjectState does not contain ProductionBrief."
            )

        if state.outline is None:
            raise ValueError(
                "ProjectState does not contain OutlineData."
            )

        if state.script is None:
            raise ValueError(
                "ProjectState does not contain ScriptData."
            )

        prompt = json.dumps(

            {
                "production_brief":
                    state.production_brief.model_dump(),

                "outline":
                    state.outline.model_dump(),

                "script":
                    state.script.model_dump(),
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        state.storyboard = StoryboardData(
            **result
        )

        return state