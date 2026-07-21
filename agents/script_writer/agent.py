"""
AIStudio Script Writer Agent

Generates the documentary script one scene at a time.

Each scene is generated independently to keep prompts small,
avoid LLM timeouts and allow failed scenes to be regenerated
without rerunning the entire script.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    ScriptData,
    ScriptSceneResponse,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("ScriptWriterAgent")


class ScriptWriterAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_scene(
        self,
        production_brief: dict,
        research: dict,
        outline_scene: dict,
    ) -> ScriptSceneResponse:
        """
        Generate one script scene.
        """

        prompt = json.dumps(
            {
                "production_brief": production_brief,
                "research": research,
                "outline_scene": outline_scene,
            },
            indent=4,
            ensure_ascii=False,
        )

        LOGGER.info(
            "Generating script scene %s",
            outline_scene["scene"],
        )

        result = self.llm.generate_json(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.25,
        )

        return ScriptSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.production_brief is None:
            raise ValueError(
                "ProductionBrief must exist before ScriptWriterAgent runs."
            )

        if state.research is None:
            raise ValueError(
                "ResearchData must exist before ScriptWriterAgent runs."
            )

        if state.outline is None:
            raise ValueError(
                "OutlineData must exist before ScriptWriterAgent runs."
            )

        LOGGER.info(
            "Starting Script Writer Agent"
        )

        production_brief = state.production_brief.model_dump()

        research = state.research.model_dump()

        script = ScriptData()

        #
        # Generate one scene at a time
        #

        for outline_scene in state.outline.scenes:

            response = self._generate_scene(

                production_brief=production_brief,

                research=research,

                outline_scene=outline_scene.model_dump(),

            )

            script.scenes.append(
                response.scene
            )

        state.script = script

        state.current_stage = "script"

        state.status = "script_complete"

        LOGGER.info(
            "Script Writer Agent completed successfully."
        )

        return state