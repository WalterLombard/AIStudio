"""
AIStudio Voice Generator Agent

Consumes the narration performance plan and generates narration audio
using TTSService or FastMCP voice generation server.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import (
    AssetRecord,
    AudioAsset,
    AudioData,
    ProjectState,
)
from shared.services import (
    AssetService,
    TTSService,
)

# Optional import of voice generation server module
try:
    from servers.voice_server import generate_narration_audio
except ImportError:
    generate_narration_audio = None

LOGGER = logging.getLogger("VoiceGeneratorAgent")


class VoiceGeneratorAgent:
    """
    Generates narration audio assets from NarrationData using TTSService or FastMCP server.
    """

    def __init__(self) -> None:
        self.tts = TTSService()
        self.assets = AssetService()

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.narration is None or not getattr(state.narration, "segments", None):
            raise ValueError(
                "VoiceGeneratorAgent failure: ProjectState does not contain valid NarrationData segments."
            )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the voice generation pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Voice Generator Agent")

        audio = AudioData()

        for idx, segment in enumerate(state.narration.segments):
            scene_id = getattr(segment, "scene_id", f"scene_{idx + 1}")
            LOGGER.info("Synthesizing narration audio for Scene %s", scene_id)

            try:
                if generate_narration_audio:
                    result = generate_narration_audio(
                        text=segment.text,
                        emotion=getattr(segment, "emotion", "neutral"),
                        speaking_rate=getattr(segment, "speaking_rate", 1.0),
                        pause_before=getattr(segment, "pause_before", 0.0),
                        pause_after=getattr(segment, "pause_after", 0.0),
                    )
                else:
                    result = self.tts.generate(
                        text=segment.text,
                        emotion=getattr(segment, "emotion", "neutral"),
                        speaking_rate=getattr(segment, "speaking_rate", 1.0),
                        pause_before=getattr(segment, "pause_before", 0.0),
                        pause_after=getattr(segment, "pause_after", 0.0),
                    )
            except Exception as err:
                raise RuntimeError(
                    f"VoiceGeneratorAgent failure during TTS synthesis for Scene {scene_id}: {err}"
                ) from err

            asset = AssetRecord(
                asset_type="audio",
                stage="voice_generation",
                provider=getattr(result, "provider", "tts"),
                filename=getattr(result, "filename", str(result)),
                source_scene=scene_id,
                duration=getattr(result, "duration", 0.0),
                metadata=getattr(result, "metadata", {}),
            )

            registered_asset = self.assets.register(asset)

            audio.assets.append(
                AudioAsset(
                    asset_id=registered_asset.asset_id,
                    scene_id=scene_id,
                    filename=registered_asset.filename,
                    duration=registered_asset.duration,
                )
            )

        # Calculate total audio duration across all generated speech assets
        audio.total_duration = sum(
            getattr(asset, "duration", 0.0) for asset in audio.assets
        )

        state.audio = audio
        state.current_stage = "voice_generation"
        state.status = "voice_complete"

        LOGGER.info("Voice Generator Agent completed successfully.")

        return state