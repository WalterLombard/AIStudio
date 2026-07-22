"""
AIStudio Visual Planner Agent

Generates the visual production plan one storyboard scene at a time
using LLM or FastMCP visual server specifications.

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

# Optional import of FastMCP visual server module
try:
    from servers.visual_server import generate_visual_scene
except ImportError:
    generate_visual_scene = None

LOGGER = logging.getLogger("VisualPlannerAgent")


class VisualPlannerAgent:
    """
    Generates the complete visual production plan.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.production_brief is None:
            raise ValueError(
                "VisualPlannerAgent failure: ProductionBrief must exist before VisualPlannerAgent runs."
            )
        if state.storyboard is None:
            raise ValueError(
                "VisualPlannerAgent failure: StoryboardData must exist before VisualPlannerAgent runs."
            )

    def _generate_scene(
        self,
        production_brief: dict,
        storyboard_scene: dict,
    ) -> VisualSceneResponse:
        """
        Generate one visual production specification.
        """
        scene_num = storyboard_scene.get("scene_number", storyboard_scene.get("scene_id", "?"))

        LOGGER.info("Generating visual plan for storyboard scene %s", scene_num)

        try:
            if generate_visual_scene:
                result = generate_visual_scene(
                    production_brief=production_brief,
                    storyboard_scene=storyboard_scene,
                )
            else:
                prompt = json.dumps(
                    {
                        "production_brief": production_brief,
                        "storyboard_scene": storyboard_scene,
                    },
                    indent=4,
                    ensure_ascii=False,
                )
                result = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=prompt,
                    temperature=0.20,
                )
        except Exception as err:
            raise RuntimeError(
                f"VisualPlannerAgent failure during generation for scene {scene_num}: {err}"
            ) from err

        try:
            if isinstance(result, VisualSceneResponse):
                return result

            # Flexible parsing: Handles both {"scene": {...}} and direct {...} outputs
            if isinstance(result, dict):
                if "scene" in result and isinstance(result["scene"], dict):
                    return VisualSceneResponse(**result)
                elif "scene" in result:
                    return VisualSceneResponse(scene=result["scene"])
                else:
                    return VisualSceneResponse(scene=result)
            else:
                return VisualSceneResponse(scene=result)
        except Exception as err:
            raise ValueError(
                f"VisualPlannerAgent failed to validate output for scene {scene_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the visual planning pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Visual Planner Agent")

        production_brief = state.production_brief.model_dump()
        visual_plan = VisualData()

        for storyboard_scene in state.storyboard.scenes:
            response = self._generate_scene(
                production_brief=production_brief,
                storyboard_scene=storyboard_scene.model_dump(),
            )

            visual_plan.scenes.append(response.scene)

        state.visuals = visual_plan
        state.current_stage = "visual_planning"
        state.status = "visual_plan_complete"

        LOGGER.info("Visual Planner Agent completed successfully.")

        return state