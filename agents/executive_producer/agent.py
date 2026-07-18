"""
AIStudio Executive Producer Agent

Responsible for creating the initial Production Brief for a project.

This is the first AI agent in the AIStudio pipeline.

Author : AIStudio
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
    Produces the Production Brief from the user's request.
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
        """
        Generate the Production Brief.

        Parameters
        ----------
        user_request
            The user's requested video.

        state
            Existing project state (optional).

        Returns
        -------
        ProjectState
        """

        if state is None:

            state = ProjectState()

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=user_request,

            temperature=0.4,

        )

        state.production_brief = ProductionBrief(**result)

        state.project.title = (
            state.production_brief.title
        )

        state.project.topic = (
            state.production_brief.topic
        )

        state.project.duration_minutes = (
            state.production_brief.duration_minutes
        )

        return state