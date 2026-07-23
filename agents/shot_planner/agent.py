"""
AIStudio Shot Planner Agent

Generates the cinematography specification one storyboard shot at a time
using LLM or FastMCP shot server specifications.

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

# Optional import of FastMCP shot server module
try:
    from servers.shot_server import generate_shot_specification
except ImportError:
    generate_shot_specification = None

LOGGER = logging.getLogger("ShotPlannerAgent")


class ShotPlannerAgent:
    """
    Produces the complete cinematography plan using compact state memory.
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
                "ShotPlannerAgent failure: ProductionBrief must exist before ShotPlannerAgent runs."
            )
        if state.storyboard is None:
            raise ValueError(
                "ShotPlannerAgent failure: StoryboardData must exist before ShotPlannerAgent runs."
            )
        if state.visuals is None:
            raise ValueError(
                "ShotPlannerAgent failure: VisualData must exist before ShotPlannerAgent runs."
            )

    def _generate_shot(
        self,
        production_brief: dict,
        visual_scene: dict | None,
        storyboard_shot: dict,
        scene_id: str,
        last_shot_spec: dict | None,
        outline_summary: list[dict],
    ) -> ShotSceneResponse:
        """
        Generate ONE shot specification using compact context payloads.
        """
        shot_num = storyboard_shot.get("shot_number", "?")

        LOGGER.info(
            "Generating shot specification for Scene %s, Shot %s",
            scene_id,
            shot_num,
        )

        try:
            if generate_shot_specification:
                result = generate_shot_specification(
                    production_brief=production_brief,
                    visual_scene=visual_scene,
                    scene_id=scene_id,
                    storyboard_shot=storyboard_shot,
                    completed_shots=[last_shot_spec] if last_shot_spec else [],
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
                        "visual_scene": visual_scene,
                        "scene_id": scene_id,
                        "storyboard_shot": storyboard_shot,
                        "previous_shot": last_shot_spec,
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
                f"ShotPlannerAgent failure during generation for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

        try:
            if isinstance(result, ShotSceneResponse):
                return result

            # Flexible parsing: Handles both {"shot": {...}} and direct {...} outputs
            if isinstance(result, dict):
                if "shot" in result and isinstance(result["shot"], dict) and "shot" in result["shot"]:
                    return ShotSceneResponse(**result)
                elif "shot" in result and isinstance(result["shot"], dict):
                    return ShotSceneResponse(shot=result["shot"])
                else:
                    return ShotSceneResponse(shot=result)
            else:
                return ShotSceneResponse(shot=result)
        except Exception as err:
            raise ValueError(
                f"ShotPlannerAgent failed to validate output for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the shot planning pipeline step using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Shot Planner Agent")

        shot_data = ShotData()
        production_brief = state.production_brief.model_dump()

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        # Build flexible lookup table by scene_id (supporting both int and str keys)
        visual_lookup = {}
        for visual in state.visuals.scenes:
            visual_dict = visual.model_dump()
            sc_id = visual_dict.get("scene_id") or getattr(visual, "scene_id", None)
            if sc_id is not None:
                visual_lookup[str(sc_id)] = visual_dict
                visual_lookup[sc_id] = visual_dict

        last_shot_spec: dict | None = None

        # Generate shot specifications scene by scene, shot by shot
        for scene in state.storyboard.scenes:
            scene_id = str(getattr(scene, "scene_number", getattr(scene, "scene_id", 1)))
            visual_scene = visual_lookup.get(scene_id) or visual_lookup.get(int(scene_id) if scene_id.isdigit() else scene_id)

            for shot in scene.shots:
                response = self._generate_shot(
                    production_brief,
                    visual_scene,
                    shot.model_dump(),
                    scene_id,
                    last_shot_spec,
                    outline_summary,
                )

                shot_data.shots.append(response.shot)
                last_shot_spec = response.shot.model_dump()

        state.shots = shot_data
        state.current_stage = "shot_planning"
        state.status = "shot_planning_complete"

        LOGGER.info("Shot Planner Agent completed successfully.")

        return state