"""
AIStudio Outline Agent

Generates the documentary outline one scene at a time using LLM
or FastMCP outline server specifications.

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
from shared.services.memory_service import ProjectMemory

# Optional import of FastMCP outline server module
try:
    from servers.outline_server import generate_outline_scene
except ImportError:
    generate_outline_scene = None

LOGGER = logging.getLogger("OutlineAgent")


class OutlineAgent:
    """
    Generates the documentary outline scene by scene utilizing project memory.
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
                "OutlineAgent failure: ProductionBrief must exist before OutlineAgent runs."
            )
        if state.research is None:
            raise ValueError(
                "OutlineAgent failure: ResearchData must exist before OutlineAgent runs."
            )

    def _generate_scene(
        self,
        production_brief: dict,
        research: dict,
        scene_number: int,
        total_scenes: int,
        scene_duration: int,
        last_scene_context: dict | None,
    ) -> OutlineSceneResponse:
        """
        Generate one outline scene with context of only the previous scene memory.
        """
        LOGGER.info("Generating outline scene %s of %s", scene_number, total_scenes)

        try:
            if generate_outline_scene:
                result = generate_outline_scene(
                    production_brief=production_brief,
                    research=research,
                    scene_number=scene_number,
                    total_scenes=total_scenes,
                    scene_duration=scene_duration,
                    completed_scenes=[last_scene_context] if last_scene_context else [],
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
                        "scene_number": scene_number,
                        "total_scenes": total_scenes,
                        "scene_duration": scene_duration,
                        "previous_scene": last_scene_context,
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
                f"OutlineAgent failure during generation for scene {scene_number}: {err}"
            ) from err

        try:
            if isinstance(result, OutlineSceneResponse):
                return result

            if isinstance(result, dict):
                if "scene" in result and isinstance(result["scene"], dict):
                    return OutlineSceneResponse(**result)
                else:
                    return OutlineSceneResponse(scene=result)
            else:
                return OutlineSceneResponse(scene=result)
        except Exception as err:
            raise ValueError(
                f"OutlineAgent failed to validate output for scene {scene_number}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the outline generation pipeline step with memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Outline Agent")

        production_brief = state.production_brief.model_dump()
        research = state.research.model_dump()

        total_duration = state.production_brief.duration_minutes * 60
        total_scenes = 10
        scene_duration = total_duration // total_scenes

        outline = OutlineData(
            title=state.production_brief.title,
            scene_count=total_scenes,
            total_duration=total_duration,
        )

        # Initialize ProjectMemory on state if not present
        if state.memory is None:
            state.memory = ProjectMemory()

        for scene_number in range(1, total_scenes + 1):
            last_scene_context = state.memory.get_preceding_scene_context(scene_number)

            response = self._generate_scene(
                production_brief=production_brief,
                research=research,
                scene_number=scene_number,
                total_scenes=total_scenes,
                scene_duration=scene_duration,
                last_scene_context=last_scene_context,
            )

            outline.scenes.append(response.scene)
            
            # Store compressed summary in centralized project memory
            state.memory.store_scene(scene_number, response.scene.model_dump())

        state.outline = outline
        state.current_stage = "outline"
        state.status = "outline_complete"

        LOGGER.info("Outline Agent completed successfully.")

        return state