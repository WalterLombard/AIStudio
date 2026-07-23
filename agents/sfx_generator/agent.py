"""
AIStudio Sound Effects Generator

Generates documentary sound effects one shot at a time.
After planning completes, uses SFXService or FastMCP SFX server
to generate the actual sound effect assets.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    AssetRecord,
    ProjectState,
    SFXAsset,
    SFXData,
    SFXLibrary,
    SFXSceneResponse,
)
from shared.services import (
    AssetService,
    LLMService,
    PromptService,
    SFXService,
)

# Optional import of FastMCP sound effects server module
try:
    from servers.sfx_server import generate_sfx_effect
except ImportError:
    generate_sfx_effect = None

LOGGER = logging.getLogger("SFXGeneratorAgent")


class SFXGeneratorAgent:
    """
    Generates documentary sound effects one shot at a time using compact state memory.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.sfx = SFXService()
        self.assets = AssetService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.motion is None or not state.motion.scenes:
            raise ValueError(
                "SFXGeneratorAgent failure: MotionData must exist before SFXGeneratorAgent runs."
            )
        if state.narration is None or not state.narration.segments:
            raise ValueError(
                "SFXGeneratorAgent failure: NarrationData must exist before SFXGeneratorAgent runs."
            )

    def _generate_cue(
        self,
        production_brief: dict | None,
        motion: dict,
        narration: dict,
        last_sfx_spec: dict | None,
        outline_summary: list[dict],
    ) -> SFXSceneResponse:
        """
        Generate sound effects for one shot using compact context payloads.
        """
        scene_id = motion.get("scene_id", narration.get("scene_id", "?"))
        shot_num = motion.get("shot_number", narration.get("shot_number", "?"))

        LOGGER.info("Generating SFX cue specification for Scene %s, Shot %s", scene_id, shot_num)

        try:
            if generate_sfx_effect and hasattr(generate_sfx_effect, "generate_cue_specification"):
                result = generate_sfx_effect(
                    production_brief=production_brief,
                    motion=motion,
                    narration=narration,
                    completed_cues=[last_sfx_spec] if last_sfx_spec else [],
                )
            else:
                prompt_payload = {
                    "motion": motion,
                    "narration": narration,
                    "outline_summary": outline_summary,
                    "previous_sfx": last_sfx_spec,
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
                f"SFXGeneratorAgent failure during cue generation for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

        try:
            # Flexible parsing: Handles {"cue": {...}}, {"cues": [...]}, and direct object responses
            if isinstance(result, SFXSceneResponse):
                return result

            if isinstance(result, dict):
                if "cue" in result and isinstance(result["cue"], dict):
                    return SFXSceneResponse(**result)
                elif "cues" in result and isinstance(result["cues"], list) and len(result["cues"]) > 0:
                    return SFXSceneResponse(cue=result["cues"][0])
                else:
                    return SFXSceneResponse(cue=result)
            elif isinstance(result, list) and len(result) > 0:
                return SFXSceneResponse(cue=result[0])
            else:
                return SFXSceneResponse(cue=result)
        except Exception as err:
            raise ValueError(
                f"SFXGeneratorAgent failed to validate output for Scene {scene_id} Shot {shot_num}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the SFX planning and audio asset generation pipeline step using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Sound Effects Generator Agent")

        plan = SFXData()
        production_brief = state.production_brief.model_dump() if state.production_brief else None

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        last_sfx_spec: dict | None = None

        # Process motion scenes and narration segments
        for motion, narration in zip(
            state.motion.scenes,
            state.narration.segments,
            strict=False,
        ):
            motion_dict = motion.model_dump() if hasattr(motion, "model_dump") else motion
            narration_dict = narration.model_dump() if hasattr(narration, "model_dump") else narration

            response = self._generate_cue(
                production_brief=production_brief,
                motion=motion_dict,
                narration=narration_dict,
                last_sfx_spec=last_sfx_spec,
                outline_summary=outline_summary,
            )

            if response and hasattr(response, "cue") and response.cue:
                plan.cues.append(response.cue)
                last_sfx_spec = response.cue.model_dump() if hasattr(response.cue, "model_dump") else response.cue

        # Generate SFX assets
        library = SFXLibrary()

        for cue in plan.cues:
            scene_id = getattr(cue, "scene_id", "1")
            shot_num = getattr(cue, "shot_number", 1)

            LOGGER.info("Synthesizing SFX asset for Scene %s, Shot %s", scene_id, shot_num)

            try:
                if generate_sfx_effect:
                    generated = generate_sfx_effect(cue=cue)
                else:
                    generated = self.sfx.generate(cue)
            except Exception as err:
                raise RuntimeError(
                    f"SFXGeneratorAgent failure during audio synthesis for Scene {scene_id} Shot {shot_num}: {err}"
                ) from err

            asset = AssetRecord(
                asset_type="sfx",
                stage="sfx_generation",
                provider=getattr(generated, "provider", "sfx_gen"),
                filename=getattr(generated, "filename", str(generated)),
                source_scene=scene_id,
                duration=getattr(generated, "duration", 0.0),
                metadata={
                    **getattr(generated, "metadata", {}),
                    "shot_number": getattr(cue, "shot_number", None),
                    "image_asset_id": getattr(cue, "image_asset_id", None),
                },
            )

            registered_asset = self.assets.register(asset)

            library.assets.append(
                SFXAsset(
                    asset_id=registered_asset.asset_id,
                    scene_id=scene_id,
                    shot_number=getattr(cue, "shot_number", 1),
                    image_asset_id=getattr(cue, "image_asset_id", ""),
                    filename=registered_asset.filename,
                    duration=registered_asset.duration,
                )
            )

        state.sfx = library
        state.current_stage = "sfx_generation"
        state.status = "sfx_complete"

        LOGGER.info("Sound Effects Generator Agent completed successfully.")

        return state