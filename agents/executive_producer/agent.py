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

    Responsibilities
    ----------------
    - Read the user's request
    - Generate the Production Brief
    - Initialise the ProjectState
    - Populate the project metadata

    This agent does NOT perform research, outlining,
    scripting or storyboarding.
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

        state.production_brief = brief

        #
        # Initialise project metadata
        #

        state.project_info.title = brief.title

        state.project_info.topic = brief.topic

        state.project_info.duration_minutes = (
            brief.duration_minutes
        )

        state.current_stage = "production_brief"

        state.status = "completed"

        return state