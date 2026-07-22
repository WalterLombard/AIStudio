"""
AIStudio Narration Designer Agent

Generates voice performance specifications shot by shot using LLM
or FastMCP narration server specifications.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    NarrationData,
    NarrationSceneResponse,
    ProjectState,
)
from shared.services import (
    LLMService,
    PromptService,
)

# Optional import of FastMCP narration server module
try:
    from servers.narration_server import generate_narration_segment
except ImportError:
    generate_narration_segment = None

LOGGER = logging.getLogger("NarrationDesignerAgent")


class NarrationDesignerAgent:
    """
    Produces voice performance and timing specifications for TTS generation.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.shots is None or not state.shots.shots:
            raise ValueError(
                "NarrationDesignerAgent failure: ShotData must exist before NarrationDesignerAgent runs."
            )
        if state.motion is None or not state.motion.scenes:
            raise ValueError(
                "NarrationDesignerAgent failure: MotionData must exist before NarrationDesignerAgent runs."
            )

    def _generate_segment(
        self,
        shot: dict,
        motion_scene: dict | None,
    ) -> NarrationSceneResponse:
        """
        Generate narration performance for one shot.
        """
        shot_num = shot.get("shot_number", "?")
        scene_id = shot.get("scene_id", "?")

        LOGGER.info("Generating narration performance for Scene %s, Shot %s", scene_id, shot_num)

        try:
            if generate_narration_segment:
                result = generate_narration_segment(
                    shot=shot,
                    motion_scene=motion_scene,
                )
            else:
                prompt = json.dumps(
                    {
                        "shot": shot,
                        "motion": motion_scene,
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
                f"NarrationDesignerAgent failure during generation for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

        try:
            if isinstance(result, NarrationSceneResponse):
                return result

            # Flexible parsing: Handles {"segments": [...]}, {"segment": {...}}, and direct array wrappers
            if isinstance(result, dict):
                if "segments" in result:
                    return NarrationSceneResponse(**result)
                elif "segment" in result:
                    segment_val = result["segment"]
                    segments_list = [segment_val] if isinstance(segment_val, dict) else segment_val
                    return NarrationSceneResponse(segments=segments_list)
                else:
                    return NarrationSceneResponse(segments=[result])
            elif isinstance(result, list):
                return NarrationSceneResponse(segments=result)
            else:
                return NarrationSceneResponse(segments=[result])
        except Exception as err:
            raise ValueError(
                f"NarrationDesignerAgent failed to validate output for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the narration performance design pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Narration Designer Agent")

        narration = NarrationData()

        # Build lookup table for motion scenes by scene_id
        motion_lookup = {}
        for motion_scene in state.motion.scenes:
            m_dict = motion_scene.model_dump()
            sc_id = m_dict.get("scene_id") or getattr(motion_scene, "scene_id", None)
            if sc_id is not None:
                motion_lookup[str(sc_id)] = m_dict

        # Process each shot independently without truncating via zip
        for shot in state.shots.shots:
            shot_dict = shot.model_dump()
            scene_id = str(shot_dict.get("scene_id", ""))
            motion_scene = motion_lookup.get(scene_id)

            response = self._generate_segment(
                shot=shot_dict,
                motion_scene=motion_scene,
            )

            # Safely unpack list of generated segments
            if hasattr(response, "segments") and response.segments:
                narration.segments.extend(response.segments)
            elif hasattr(response, "segment") and response.segment:
                narration.segments.append(response.segment)

        state.narration = narration
        state.current_stage = "narration"
        state.status = "narration_complete"

        LOGGER.info("Narration Designer Agent completed successfully.")

        return state