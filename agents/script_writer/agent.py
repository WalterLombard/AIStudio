"""
AIStudio Script Writer Agent

Generates the complete documentary narration from the approved outline.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    ProjectState,
    ScriptData,
)

from shared.services import (
    LLMService,
    PromptService,
)


class ScriptWriterAgent:
    """
    Produces the complete documentary script.
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

        if state.research is None:
            raise ValueError(
                "ProjectState does not contain ResearchData."
            )

        if state.outline is None:
            raise ValueError(
                "ProjectState does not contain OutlineData."
            )

        prompt = json.dumps(

            {
                "production_brief":
                    state.production_brief.model_dump(),

                "research":
                    state.research.model_dump(),

                "outline":
                    state.outline.model_dump(),
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.25,

        )

        state.script = ScriptData(
            **result
        )

        return state