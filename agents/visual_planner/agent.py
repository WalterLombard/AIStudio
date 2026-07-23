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
    Generates the complete visual production plan utilizing project memory context.
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
        last_visual_scene: dict | None,
        outline_summary: list[dict],
    ) -> VisualSceneResponse:
        """
        Generate one visual production specification with compact context payloads.
        """
        scene_num = storyboard_scene.get("scene_number", storyboard_scene.get("scene_id", "?"))

        LOGGER.info("Generating visual plan for storyboard scene %s", scene_num)

        try:
            if generate_visual_scene:
                result = generate_visual_scene(
                    production_brief=production_brief,
                    storyboard_scene=storyboard_scene,
                    completed_scenes=[last_visual_scene] if last_visual_scene else [],
                )
            else:
                prompt = json.dumps(
                    {
                        "production_brief": {
                            "title": production_brief.get("title"),
                            "topic": production_brief.get("topic"),
                            "tone": production_brief.get("tone"),
                            "story_arc": production_brief.get("story_arc"),
                        },
                        "outline_summary": outline_summary,
                        "storyboard_scene": storyboard_scene,
                        "previous_visual_scene": last_visual_scene,
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
        Executes the visual planning pipeline step using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Visual Planner Agent")

        production_brief = state.production_brief.model_dump()
        visual_plan = VisualData()

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        last_visual_scene: dict | None = None

        for storyboard_scene in state.storyboard.scenes:
            scene_dict = storyboard_scene.model_dump()

            response = self._generate_scene(
                production_brief=production_brief,
                storyboard_scene=scene_dict,
                last_visual_scene=last_visual_scene,
                outline_summary=outline_summary,
            )

            visual_plan.scenes.append(response.scene)
            last_visual_scene = response.scene.model_dump()

        state.visuals = visual_plan
        state.current_stage = "visual_planning"
        state.status = "visual_plan_complete"

        LOGGER.info("Visual Planner Agent completed successfully.")

        return state