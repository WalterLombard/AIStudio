"""
AIStudio Visual Planner Agent

Generates the visual production plan one storyboard scene at a time.

Each storyboard scene produces exactly one visual production
specification. This keeps prompts small, avoids LLM timeouts and
allows failed scenes to be regenerated independently.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    VisualData,
    VisualSceneResponse,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("VisualPlannerAgent")


class VisualPlannerAgent:
    """
    Generates the complete visual production plan.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_scene(
        self,
        production_brief: dict,
        storyboard_scene: dict,
    ) -> VisualSceneResponse:
        """
        Generate one visual production specification.
        """

        prompt = json.dumps(

            {
                "production_brief": production_brief,
                "storyboard_scene": storyboard_scene,
            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(

            "Generating visual plan for storyboard scene %s",

            storyboard_scene.get(
                "scene_number",
                "?",
            ),

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return VisualSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

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

        production_brief = (
            state.production_brief.model_dump()
        )

        visual_plan = VisualData()

        #
        # Generate one visual specification per storyboard scene
        #

        for storyboard_scene in state.storyboard.scenes:

            response = self._generate_scene(

                production_brief=production_brief,

                storyboard_scene=storyboard_scene.model_dump(),

            )

            visual_plan.scenes.append(
                response.scene
            )

        state.visuals = visual_plan

        state.current_stage = "visual_planning"

        state.status = "visual_plan_complete"

        LOGGER.info(
            "Visual Planner Agent completed successfully."
        )

        return state