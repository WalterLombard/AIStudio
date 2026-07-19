"""
AIStudio Outline Agent

Creates the complete documentary structure from the Production Brief
and Research package.

The Outline is the blueprint for the Script Writer and determines
the pacing, narrative flow, emotional progression and viewer retention.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    OutlineData,
    ProjectState,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("OutlineAgent")


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
            __file__,
        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Generate the documentary outline.

        Parameters
        ----------
        state
            Current project state.

        Returns
        -------
        Updated ProjectState
        """

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief must exist before OutlineAgent runs."
            )

        if state.research is None:

            raise ValueError(
                "ResearchData must exist before OutlineAgent runs."
            )

        LOGGER.info(
            "Starting Outline Agent"
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

        outline = OutlineData(**result)

        state.outline = outline

        state.current_stage = "outline"

        state.status = "outline_complete"

        LOGGER.info(
            "Outline Agent completed successfully."
        )

        return state