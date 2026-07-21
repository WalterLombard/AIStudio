"""
AIStudio Executive Producer Agent

Creates the initial Production Brief from the user's request.

This is the first AI agent in the AIStudio production pipeline.

Author: AIStudio
"""

from __future__ import annotations

from shared.models import (
    ProjectState,
    ProductionBrief,
)

from shared.services import (
    LLMService,
    PromptService,
)


class ExecutiveProducer:
    """
    Generates the initial Production Brief.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def run(
        self,
        user_request: str,
        state: ProjectState | None = None,
    ) -> ProjectState:

        if state is None:
            state = ProjectState()

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=user_request,

            temperature=0.4,

        )

        brief = ProductionBrief(**result)

        #
        # Store the production brief
        #

        state.production_brief = brief

        #
        # Populate project metadata
        #

        state.project_info.project_name = brief.title

        state.project_info.topic = brief.topic

        #
        # Update pipeline state
        #

        state.current_stage = "production_brief"

        state.status = "production_brief_complete"

        return state