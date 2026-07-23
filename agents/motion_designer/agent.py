"""
AIStudio Motion Designer Agent

Generates the cinematic motion plan one shot at a time using LLM
or FastMCP motion server specifications.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    MotionData,
    MotionSceneResponse,
    ProjectState,
)
from shared.services import (
    AssetService,
    LLMService,
    PromptService,
)

# Optional import of FastMCP motion server module
try:
    from servers.motion_server import generate_shot_motion
except ImportError:
    generate_shot_motion = None

LOGGER = logging.getLogger("MotionDesignerAgent")


class MotionDesignerAgent:
    """
    Produces camera movement and post-processing animation specifications using compact state memory.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.assets = AssetService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.shots is None or not state.shots.shots:
            raise ValueError(
                "MotionDesignerAgent failure: ShotData must exist before MotionDesignerAgent runs."
            )

    def _generate_motion(
        self,
        production_brief: dict | None,
        shot: dict,
        image_asset: dict,
        last_motion_spec: dict | None,
        outline_summary: list[dict],
    ) -> MotionSceneResponse:
        """
        Generate motion for one approved shot using compact context payloads.
        """
        shot_num = shot.get("shot_number", "?")
        scene_id = shot.get("scene_id", "?")

        LOGGER.info("Generating motion for Scene %s, Shot %s", scene_id, shot_num)

        try:
            if generate_shot_motion:
                result = generate_shot_motion(
                    production_brief=production_brief,
                    shot=shot,
                    image_asset=image_asset,
                    completed_motions=[last_motion_spec] if last_motion_spec else [],
                )
            else:
                prompt_payload = {
                    "shot": shot,
                    "image_asset": image_asset,
                    "outline_summary": outline_summary,
                    "previous_motion": last_motion_spec,
                }
                if production_brief:
                    prompt_payload["production_brief"] = {
                        "title": production_brief.get("title"),
                        "topic": production_brief.get("topic"),
                        "tone": production_brief.get("tone"),
                    }

                prompt = json.dumps(
                    prompt_payload,
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
                f"MotionDesignerAgent failure during generation for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

        try:
            # Handle if result is already a MotionSceneResponse instance
            if isinstance(result, MotionSceneResponse):
                return result

            # Flexible parsing: Handles {"scenes": [...]}, {"scene": {...}}, and direct array wrappers
            if isinstance(result, dict):
                if "scenes" in result:
                    return MotionSceneResponse(**result)
                elif "scene" in result:
                    scene_val = result["scene"]
                    scenes_list = [scene_val] if isinstance(scene_val, dict) else scene_val
                    return MotionSceneResponse(scenes=scenes_list)
                else:
                    return MotionSceneResponse(scenes=[result])
            elif isinstance(result, list):
                return MotionSceneResponse(scenes=result)
            else:
                return MotionSceneResponse(scenes=[result])
        except Exception as err:
            raise ValueError(
                f"MotionDesignerAgent failed to validate output for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the motion design pipeline step using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Motion Designer Agent")

        motion = MotionData()
        production_brief = state.production_brief.model_dump() if state.production_brief else None

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        # Retrieve available image assets
        raw_assets = self.assets.get_assets_by_type("image")
        image_assets_map = {}
        for idx, asset in enumerate(raw_assets):
            asset_dict = asset.model_dump() if hasattr(asset, "model_dump") else asset
            # Index by asset_id, shot_number, or sequential index
            key = str(asset_dict.get("asset_id", asset_dict.get("shot_number", idx)))
            image_assets_map[key] = asset_dict

        last_motion_spec: dict | None = None

        # Process every shot without truncation
        for idx, shot in enumerate(state.shots.shots):
            shot_dict = shot.model_dump()
            shot_num = str(shot_dict.get("shot_number", idx))
            
            # Lookup asset or supply default metadata wrapper
            image_asset = image_assets_map.get(
                shot_num,
                {"asset_id": f"asset_shot_{shot_num}", "path": ""}
            )

            response = self._generate_motion(
                production_brief=production_brief,
                shot=shot_dict,
                image_asset=image_asset,
                last_motion_spec=last_motion_spec,
                outline_summary=outline_summary,
            )

            # Safely append generated motion entries
            if hasattr(response, "scenes") and response.scenes:
                motion.scenes.extend(response.scenes)
                if response.scenes:
                    last_motion_spec = response.scenes[-1].model_dump() if hasattr(response.scenes[-1], "model_dump") else response.scenes[-1]
            elif hasattr(response, "scene") and response.scene:
                motion.scenes.append(response.scene)
                last_motion_spec = response.scene.model_dump() if hasattr(response.scene, "model_dump") else response.scene

        # Calculate total duration
        motion.total_duration = sum(
            getattr(scene, "duration", 0.0) for scene in motion.scenes
        )

        state.motion = motion
        state.current_stage = "motion"
        state.status = "motion_complete"

        LOGGER.info("Motion Designer Agent completed successfully.")

        return state