"""
AIStudio Music Generator Agent

Generates the documentary music plan one shot at a time.
Triggers music audio generation using MusicService or FastMCP music server.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    AssetRecord,
    MusicAsset,
    MusicData,
    MusicLibrary,
    MusicSceneResponse,
    ProjectState,
)
from shared.services import (
    AssetService,
    LLMService,
    MusicService,
    PromptService,
)

# Optional import of FastMCP music server tool
try:
    from servers.music_server import generate_music_track
except ImportError:
    generate_music_track = None

LOGGER = logging.getLogger("MusicGeneratorAgent")


class MusicGeneratorAgent:
    """
    Produces background music specifications and triggers music audio generation.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.music = MusicService()
        self.assets = AssetService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.motion is None or not state.motion.scenes:
            raise ValueError(
                "MusicGeneratorAgent failure: MotionData must exist before MusicGeneratorAgent runs."
            )
        if state.narration is None or not state.narration.segments:
            raise ValueError(
                "MusicGeneratorAgent failure: NarrationData must exist before MusicGeneratorAgent runs."
            )

    def _generate_cue(
        self,
        motion: dict,
        narration: dict,
    ) -> MusicSceneResponse:
        """
        Generate one music cue specification.
        """
        scene_id = motion.get("scene_id", narration.get("scene_id", "?"))

        prompt = json.dumps(
            {
                "motion": motion,
                "narration": narration,
            },
            indent=4,
            ensure_ascii=False,
        )

        LOGGER.info("Generating music cue specification for Scene %s", scene_id)

        result = self.llm.generate_json(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.20,
        )

        try:
            # Flexible parsing: Handles {"cues": [...]}, {"cue": {...}}, and direct array wrappers
            if "cues" in result:
                return MusicSceneResponse(**result)
            elif "cue" in result:
                cue_val = result["cue"]
                cues_list = [cue_val] if isinstance(cue_val, dict) else cue_val
                return MusicSceneResponse(cues=cues_list)
            else:
                cues_list = [result] if isinstance(result, dict) else result
                return MusicSceneResponse(cues=cues_list)
        except Exception as err:
            raise ValueError(
                f"MusicGeneratorAgent failed to validate output for Scene {scene_id}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the music design and audio generation pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Music Generator Agent")

        music_plan = MusicData()

        # Build lookup table for narration segments by scene_id / index
        narration_map = {
            str(seg.model_dump().get("scene_id", idx)): seg.model_dump()
            for idx, seg in enumerate(state.narration.segments)
        }

        # Process motion scenes to generate musical cues
        for idx, motion_scene in enumerate(state.motion.scenes):
            motion_dict = motion_scene.model_dump()
            scene_id = str(motion_dict.get("scene_id", idx))
            narration_dict = narration_map.get(scene_id, {})

            response = self._generate_cue(
                motion=motion_dict,
                narration=narration_dict,
            )

            # Safely append generated cue entries
            if hasattr(response, "cues") and response.cues:
                music_plan.cues.extend(response.cues)
            elif hasattr(response, "cue") and response.cue:
                music_plan.cues.append(response.cue)

        # Generate audio assets from cues and register them
        library = MusicLibrary()

        for cue in music_plan.cues:
            scene_id = getattr(cue, "scene_id", "1")
            LOGGER.info("Synthesizing music audio asset for Scene %s", scene_id)

            try:
                if generate_music_track:
                    generated = generate_music_track(cue=cue)
                else:
                    generated = self.music.generate(cue)
            except Exception as err:
                raise RuntimeError(
                    f"MusicGeneratorAgent failure during audio synthesis for Scene {scene_id}: {err}"
                ) from err

            asset = AssetRecord(
                asset_type="music",
                stage="music_generation",
                provider=getattr(generated, "provider", "music_gen"),
                filename=getattr(generated, "filename", str(generated)),
                source_scene=scene_id,
                duration=getattr(generated, "duration", 0.0),
                metadata=getattr(generated, "metadata", {}),
            )

            registered_asset = self.assets.register(asset)

            library.assets.append(
                MusicAsset(
                    asset_id=registered_asset.asset_id,
                    scene_id=scene_id,
                    filename=registered_asset.filename,
                    duration=registered_asset.duration,
                )
            )

        state.music = library
        state.current_stage = "music_generation"
        state.status = "music_complete"

        LOGGER.info("Music Generator Agent completed successfully.")

        return state