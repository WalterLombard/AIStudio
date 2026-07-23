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
    Generates documentary narration scene by scene utilizing project memory.
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
        last_script_scene: dict | None,
        outline_summary: list[dict],
    ) -> ScriptSceneResponse:
        """
        Generate one script scene using concise state memory and the current outline scene.
        """
        scene_num = outline_scene.get("scene_number", outline_scene.get("scene", "Unknown"))
        LOGGER.info("Generating script scene %s", scene_num)

        try:
            if generate_script_scene:
                result = generate_script_scene(
                    production_brief=production_brief,
                    research=research,
                    outline_scene=outline_scene,
                    completed_scenes=[last_script_scene] if last_script_scene else [],
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
                        "research_topics": research.get("search_keywords", []),
                        "outline_summary": outline_summary,
                        "current_outline_scene": outline_scene,
                        "previous_script_scene": last_script_scene,
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
        Executes the script writing pipeline step using project memory.
        """
        self._validate_state(state)

        LOGGER.info("Starting Script Writer Agent")

        production_brief = state.production_brief.model_dump()
        research = state.research.model_dump()
        script = ScriptData()

        # Retrieve outline overview from memory if available, or generate a fallback compact list
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory
            else [{"scene_number": s.scene_number, "title": s.title, "goal": s.goal} for s in state.outline.scenes]
        )

        last_script_scene: dict | None = None

        for outline_scene in state.outline.scenes:
            scene_dict = outline_scene.model_dump()
            scene_num = scene_dict.get("scene_number")

            response = self._generate_scene(
                production_brief=production_brief,
                research=research,
                outline_scene=scene_dict,
                last_script_scene=last_script_scene,
                outline_summary=outline_summary,
            )

            script.scenes.append(response.scene)
            last_script_scene = response.scene.model_dump()

            # Optional: store script segment summary in state.memory if desired for subsequent agents
            if state.memory and scene_num:
                # You can store or track script milestones here if needed
                pass

        state.script = script
        state.current_stage = "script"
        state.status = "script_complete"

        LOGGER.info("Script Writer Agent completed successfully.")

        return state