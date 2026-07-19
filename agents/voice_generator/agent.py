"""
AIStudio Voice Generator Agent

Consumes the narration performance plan and generates narration audio.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    AudioAsset,
    AudioData,
    AssetRecord,
    ProjectState,
)

from shared.services import (
    AssetService,
    TTSService,
)


class VoiceGeneratorAgent:
    """
    Generates narration audio from NarrationData.
    """

    def __init__(self) -> None:

        self.tts = TTSService()

        self.assets = AssetService()

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.narration is None:

            raise ValueError(
                "ProjectState does not contain NarrationData."
            )

        audio = AudioData()

        for segment in state.narration.segments:

            result = self.tts.generate(

                text=segment.text,

                emotion=segment.emotion,

                speaking_rate=segment.speaking_rate,

                pause_before=segment.pause_before,

                pause_after=segment.pause_after,

            )

            asset = AssetRecord(

                asset_type="audio",

                stage="voice_generation",

                provider=result.provider,

                filename=result.filename,

                source_scene=segment.scene_id,

                duration=result.duration,

                metadata=result.metadata,

            )

            asset = self.assets.register(
                asset
            )

            audio.assets.append(

                AudioAsset(

                    asset_id=asset.asset_id,

                    scene_id=segment.scene_id,

                    filename=asset.filename,

                    duration=asset.duration,

                )

            )

        state.audio = audio

        state.current_stage = "voice_generation"

        state.status = "voice_complete"

        return state