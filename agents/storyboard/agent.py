"""
AIStudio Storyboard Agent

Generates the storyboard one scene at a time using LLM
or FastMCP storyboard server specifications.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    StoryboardData,
    StoryboardSceneResponse,
)
from shared.services import (
    LLMService,
    PromptService,
)

# Optional import of FastMCP storyboard server module
try:
    from servers.storyboard_server import generate_storyboard_scene
except ImportError:
    generate_storyboard_scene = None

LOGGER = logging.getLogger("StoryboardAgent")


class StoryboardAgent:
    """
    Generates scene-level storyboard shot outlines.
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
                "StoryboardAgent failure: ProductionBrief must exist before StoryboardAgent runs."
            )
        if state.outline is None:
            raise ValueError(
                "StoryboardAgent failure: OutlineData must exist before StoryboardAgent runs."
            )
        if state.script is None:
            raise ValueError(
                "StoryboardAgent failure: ScriptData must exist before StoryboardAgent runs."
            )

    def _generate_scene(
        self,
        production_brief: dict,
        outline_scene: dict | None,
        script_scene: dict,
    ) -> StoryboardSceneResponse:
        """
        Generate ONE storyboard scene.
        """
        scene_num = script_scene.get(
            "scene_number", script_scene.get("scene", "Unknown")
        )

        LOGGER.info("Generating storyboard scene %s", scene_num)

        try:
            if generate_storyboard_scene:
                result = generate_storyboard_scene(
                    production_brief=production_brief,
                    outline_scene=outline_scene,
                    script_scene=script_scene,
                )
            else:
                prompt = json.dumps(
                    {
                        "production_brief": production_brief,
                        "outline_scene": outline_scene,
                        "script_scene": script_scene,
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
                f"StoryboardAgent failure during generation for scene {scene_num}: {err}"
            ) from err

        try:
            if isinstance(result, StoryboardSceneResponse):
                return result

            # Flexible parsing: Handles both {"scene": {...}} and direct {...} outputs
            if isinstance(result, dict):
                if "scene" in result and isinstance(result["scene"], dict):
                    return StoryboardSceneResponse(**result)
                elif "scene" in result:
                    return StoryboardSceneResponse(scene=result["scene"])
                else:
                    return StoryboardSceneResponse(scene=result)
            else:
                return StoryboardSceneResponse(scene=result)
        except Exception as err:
            raise ValueError(
                f"StoryboardAgent failed to validate output for scene {scene_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the storyboard generation pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Storyboard Agent")

        storyboard = StoryboardData()
        production_brief = state.production_brief.model_dump()

        # Build lookup table from outline.scenes
        outline_lookup = {}
        if hasattr(state.outline, "scenes") and state.outline.scenes:
            for scene in state.outline.scenes:
                outline_lookup[scene.scene_number] = scene.model_dump()

        # Generate storyboard scene-by-scene
        for script_scene in state.script.scenes:
            scene_number = getattr(script_scene, "scene_number", None) or getattr(script_scene, "scene", None) or (len(storyboard.scenes) + 1)
            outline_scene = outline_lookup.get(scene_number)

            response = self._generate_scene(
                production_brief,
                outline_scene,
                script_scene.model_dump(),
            )

            storyboard.scenes.append(response.scene)

        state.storyboard = storyboard
        state.current_stage = "storyboard"
        state.status = "storyboard_complete"

        LOGGER.info("Storyboard Agent completed successfully.")

        return state