"""
AIStudio Script Writer Agent

Generates the documentary script one scene at a time using LLM
or FastMCP script server specifications.

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

# Optional import of FastMCP script server module
try:
    from servers.writer_server import generate_script_scene
except ImportError:
    try:
        from servers.script_server import generate_script_scene
    except ImportError:
        generate_script_scene = None

LOGGER = logging.getLogger("ScriptWriterAgent")


class ScriptWriterAgent:
    """
    Generates documentary narration scene by scene.
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
                "ScriptWriterAgent failure: ProductionBrief must exist before ScriptWriterAgent runs."
            )
        if state.research is None:
            raise ValueError(
                "ScriptWriterAgent failure: ResearchData must exist before ScriptWriterAgent runs."
            )
        if state.outline is None:
            raise ValueError(
                "ScriptWriterAgent failure: OutlineData must exist before ScriptWriterAgent runs."
            )

    def _generate_scene(
        self,
        production_brief: dict,
        research: dict,
        outline_scene: dict,
        completed_scenes: list[dict],
    ) -> ScriptSceneResponse:
        """
        Generate one script scene with context of previously generated narration.
        """
        scene_num = outline_scene.get("scene_number", outline_scene.get("scene", "Unknown"))
        LOGGER.info("Generating script scene %s", scene_num)

        try:
            if generate_script_scene:
                result = generate_script_scene(
                    production_brief=production_brief,
                    research=research,
                    outline_scene=outline_scene,
                    completed_scenes=completed_scenes,
                )
            else:
                prompt = json.dumps(
                    {
                        "production_brief": production_brief,
                        "research": research,
                        "outline_scene": outline_scene,
                        "completed_scenes": completed_scenes,
                    },
                    indent=4,
                    ensure_ascii=False,
                )
                result = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=prompt,
                    temperature=0.25,
                )
        except Exception as err:
            raise RuntimeError(
                f"ScriptWriterAgent failure during generation for scene {scene_num}: {err}"
            ) from err

        try:
            if isinstance(result, ScriptSceneResponse):
                return result

            # Flexible parsing: Handles both {"scene": {...}} and direct {...} outputs
            if isinstance(result, dict):
                if "scene" in result and isinstance(result["scene"], dict):
                    return ScriptSceneResponse(**result)
                else:
                    return ScriptSceneResponse(scene=result)
            else:
                return ScriptSceneResponse(scene=result)
        except Exception as err:
            raise ValueError(
                f"ScriptWriterAgent failed to validate output for scene {scene_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the script writing pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Script Writer Agent")

        production_brief = state.production_brief.model_dump()
        research = state.research.model_dump()
        script = ScriptData()
        completed_scenes: list[dict] = []

        for outline_scene in state.outline.scenes:
            scene_dict = outline_scene.model_dump()

            response = self._generate_scene(
                production_brief=production_brief,
                research=research,
                outline_scene=scene_dict,
                completed_scenes=completed_scenes,
            )

            script.scenes.append(response.scene)
            completed_scenes.append(response.scene.model_dump())

        state.script = script
        state.current_stage = "script"
        state.status = "script_complete"

        LOGGER.info("Script Writer Agent completed successfully.")

        return state