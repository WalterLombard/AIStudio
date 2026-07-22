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
    Generates documentary sound effects one shot at a time.
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
        motion: dict,
        narration: dict,
        production_brief: dict | None = None,
    ) -> SFXSceneResponse:
        """
        Generate sound effects for one shot.
        """
        scene_id = motion.get("scene_id", narration.get("scene_id", "?"))
        shot_num = motion.get("shot_number", narration.get("shot_number", "?"))

        prompt = json.dumps(
            {
                "production_brief": production_brief or {},
                "motion": motion,
                "narration": narration,
            },
            indent=4,
            ensure_ascii=False,
        )

        LOGGER.info("Generating SFX cue specification for Scene %s, Shot %s", scene_id, shot_num)

        result = self.llm.generate_json(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.20,
        )

        try:
            # Flexible parsing: Handles {"cue": {...}}, {"cues": [...]}, and direct object responses
            if "cue" in result and isinstance(result["cue"], dict):
                return SFXSceneResponse(**result)
            elif "cues" in result and isinstance(result["cues"], list) and len(result["cues"]) > 0:
                return SFXSceneResponse(cue=result["cues"][0])
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
        Executes the SFX planning and audio asset generation pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Sound Effects Generator Agent")

        plan = SFXData()
        production_brief = state.production_brief.model_dump() if state.production_brief else {}

        # Process motion scenes and narration segments
        for motion, narration in zip(
            state.motion.scenes,
            state.narration.segments,
            strict=False,
        ):
            response = self._generate_cue(
                motion=motion.model_dump(),
                narration=narration.model_dump(),
                production_brief=production_brief,
            )

            plan.cues.append(response.cue)

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