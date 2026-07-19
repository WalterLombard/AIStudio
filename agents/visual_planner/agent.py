"""
AIStudio Visual Planner Agent

Converts the cinematic storyboard into a complete visual production
plan.

The Visual Planner determines every visual asset required for the
production before image generation begins.

Output:
    VisualData

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    VisualData,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("VisualPlannerAgent")


class VisualPlannerAgent:
    """
    Produces the complete visual production plan.

    Input
    -----
    ProductionBrief
    StoryboardData

    Output
    ------
    VisualData
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
        Generate the visual production plan.

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
                "ProductionBrief must exist before VisualPlannerAgent runs."
            )

        if state.storyboard is None:

            raise ValueError(
                "StoryboardData must exist before VisualPlannerAgent runs."
            )

        LOGGER.info(
            "Starting Visual Planner Agent"
        )

        prompt = json.dumps(

            {
                "production_brief":
                    state.production_brief.model_dump(),

                "storyboard":
                    state.storyboard.model_dump(),
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        visual_plan = VisualData(**result)

        state.visuals = visual_plan

        state.current_stage = "visual_planning"

        state.status = "visual_plan_complete"

        LOGGER.info(
            "Visual Planner Agent completed successfully."
        )

        return state