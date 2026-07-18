"""
AIStudio Research Agent

Responsible for collecting factual research that will be used by all
downstream agents.

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
    Produces the factual research package for a project.
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
        """
        Generate research from the production brief.
        """

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief has not been generated."
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