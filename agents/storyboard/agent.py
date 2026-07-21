"""
AIStudio Storyboard Agent

Generates the storyboard one scene at a time.

This keeps prompts small, avoids LLM timeouts and allows failed
scenes to be regenerated independently.

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

LOGGER = logging.getLogger("StoryboardAgent")


class StoryboardAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_scene(
        self,
        production_brief: dict,
        outline_scene: dict | None,
        script_scene: dict,
    ):
        """
        Generate ONE storyboard scene.
        """

        prompt = json.dumps(

            {
                "production_brief": production_brief,
                "outline_scene": outline_scene,
                "script_scene": script_scene,
            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(
            "Generating storyboard scene %s",
            script_scene.get("scene", "?"),
        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return StoryboardSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.production_brief is None:
            raise ValueError(
                "ProductionBrief must exist before StoryboardAgent runs."
            )

        if state.outline is None:
            raise ValueError(
                "OutlineData must exist before StoryboardAgent runs."
            )

        if state.script is None:
            raise ValueError(
                "ScriptData must exist before StoryboardAgent runs."
            )

        LOGGER.info(
            "Starting Storyboard Agent"
        )

        storyboard = StoryboardData()

        production_brief = state.production_brief.model_dump()

        outline_lookup = {}

        #
        # Build lookup table from outline
        #

        if hasattr(state.outline, "sections"):

            for section in state.outline.sections:

                outline_lookup[section.scene_number] = (
                    section.model_dump()
                )

        #
        # Generate storyboard scene-by-scene
        #

        for script_scene in state.script.scenes:

            #
            # Determine scene number
            #

            if hasattr(script_scene, "scene_number"):

                scene_number = script_scene.scene_number

            elif hasattr(script_scene, "scene"):

                scene_number = script_scene.scene

            else:

                scene_number = len(storyboard.scenes) + 1

            outline_scene = outline_lookup.get(
                scene_number
            )

            response = self._generate_scene(

                production_brief,

                outline_scene,

                script_scene.model_dump(),

            )

            storyboard.scenes.append(
                response.scene
            )

        state.storyboard = storyboard

        state.current_stage = "storyboard"

        state.status = "storyboard_complete"

        LOGGER.info(
            "Storyboard Agent completed successfully."
        )

        return state