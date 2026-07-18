"""
AIStudio Outline Agent

Builds the documentary structure from the Production Brief and
Research results.

Produces an OutlineData object that becomes the blueprint for the
Script Writer.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    OutlineData,
    ProjectState,
)

from shared.services import (
    LLMService,
    PromptService,
)


class OutlineAgent:
    """
    Produces the documentary outline.

    Input
    -----
    ProductionBrief
    ResearchData

    Output
    ------
    OutlineData
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
        """
        Builds the documentary outline.
        """

        if state.production_brief is None:

            raise ValueError(
                "ProjectState does not contain a ProductionBrief."
            )

        if state.research is None:

            raise ValueError(
                "ProjectState does not contain ResearchData."
            )

        prompt = json.dumps(

            {
                "production_brief":
                    state.production_brief.model_dump(),

                "research":
                    state.research.model_dump(),
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.2,

        )

        state.outline = OutlineData(**result)

        return state