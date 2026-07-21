"""
AIStudio Shot Planner Agent

Generates the cinematography specification one storyboard shot at a time.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    ShotData,
    ShotSceneResponse,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("ShotPlannerAgent")


class ShotPlannerAgent:
    """
    Produces the complete cinematography plan.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_shot(
        self,
        production_brief: dict,
        visual_scene: dict | None,
        storyboard_shot: dict,
        scene_id: str,
    ) -> ShotSceneResponse:
        """
        Generate ONE shot specification.
        """

        prompt = json.dumps(

            {

                "production_brief": production_brief,

                "visual_scene": visual_scene,

                "scene_id": scene_id,

                "storyboard_shot": storyboard_shot,

            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(
            "Generating shot specification %s",
            storyboard_shot.get("shot_number", "?"),
        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return ShotSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief must exist before ShotPlannerAgent runs."
            )

        if state.storyboard is None:

            raise ValueError(
                "StoryboardData must exist before ShotPlannerAgent runs."
            )

        if state.visuals is None:

            raise ValueError(
                "VisualData must exist before ShotPlannerAgent runs."
            )

        LOGGER.info(
            "Starting Shot Planner Agent"
        )

        shot_data = ShotData()

        production_brief = (
            state.production_brief.model_dump()
        )

        visual_lookup = {}

        #
        # Build lookup table by scene_id
        #

        for visual in state.visuals.scenes:

            visual_lookup[visual.scene_id] = (
                visual.model_dump()
            )

        #
        # Generate one shot at a time
        #

        for scene in state.storyboard.scenes:

            scene_id = str(scene.scene_number)

            visual_scene = visual_lookup.get(
                scene_id
            )

            for shot in scene.shots:

                response = self._generate_shot(

                    production_brief,

                    visual_scene,

                    shot.model_dump(),

                    scene_id,

                )

                shot_data.shots.append(
                    response.shot
                )

        state.shots = shot_data

        state.current_stage = "shot_planning"

        state.status = "shot_planning_complete"

        LOGGER.info(
            "Shot Planner Agent completed successfully."
        )

        return state