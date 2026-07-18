"""
AIStudio Research Agent

Builds a comprehensive documentary research package from the
Production Brief.

Produces a ResearchData object that becomes the factual foundation
for the Outline Agent.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    ProjectState,
    ResearchData,
)

from shared.services import (
    LLMService,
    PromptService,
)


class ResearchAgent:
    """
    Produces documentary research.

    Input
    -----
    ProductionBrief

    Output
    ------
    ResearchData
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
        Generate documentary research.
        """

        if state.production_brief is None:

            raise ValueError(
                "ProjectState does not contain a ProductionBrief."
            )

        prompt = json.dumps(

            state.production_brief.model_dump(),

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.2,

        )

        state.research = ResearchData(**result)

        return state