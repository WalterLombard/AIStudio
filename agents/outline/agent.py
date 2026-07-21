"""
AIStudio Outline Agent

Generates the documentary outline one scene at a time.

Each scene is generated independently to keep prompts small,
avoid LLM timeouts and allow failed scenes to be regenerated
without rerunning the entire outline.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    OutlineData,
    OutlineSceneResponse,
    ProjectState,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("OutlineAgent")


class OutlineAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_scene(
        self,
        production_brief: dict,
        research: dict,
        scene_number: int,
        total_scenes: int,
        scene_duration: int,
    ) -> OutlineSceneResponse:
        """
        Generate one outline scene.
        """

        prompt = json.dumps(

            {
                "production_brief": production_brief,
                "research": research,
                "scene_number": scene_number,
                "total_scenes": total_scenes,
                "scene_duration": scene_duration,
            },

            indent=4,

            ensure_ascii=False,

        )

        LOGGER.info(
            "Generating outline scene %s",
            scene_number,
        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return OutlineSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

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

        production_brief = state.production_brief.model_dump()

        research = state.research.model_dump()

        total_duration = (
            state.production_brief.duration_minutes * 60
        )

        #
        # Initial implementation:
        # Fixed scene count.
        #

        total_scenes = 10

        scene_duration = total_duration // total_scenes

        outline = OutlineData(

            title=state.production_brief.title,

            scene_count=total_scenes,

            total_duration=total_duration,

        )

        #
        # Generate one scene at a time
        #

        for scene_number in range(1, total_scenes + 1):

            response = self._generate_scene(

                production_brief=production_brief,

                research=research,

                scene_number=scene_number,

                total_scenes=total_scenes,

                scene_duration=scene_duration,

            )

            outline.scenes.append(
                response.scene
            )

        state.outline = outline

        state.current_stage = "outline"

        state.status = "outline_complete"

        LOGGER.info(
            "Outline Agent completed successfully."
        )

        return state