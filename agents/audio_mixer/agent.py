"""
AIStudio Audio Mixer Agent

Produces the final mastered soundtrack.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    AssetRecord,
    ProjectState,
)

from shared.services import (
    AssetService,
    AudioMixerService,
)


class AudioMixerAgent:

    def __init__(self) -> None:

        self.assets = AssetService()

        self.mixer = AudioMixerService()

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.audio is None:

            raise ValueError(
                "Narration audio has not been generated."
            )

        if state.music is None:

            raise ValueError(
                "Music has not been generated."
            )

        if state.sfx is None:

            raise ValueError(
                "Sound effects have not been generated."
            )

        master = self.mixer.mix(

            narration=state.audio,

            music=state.music,

            sfx=state.sfx,

        )

        asset = AssetRecord(

            asset_type="master_audio",

            stage="audio_mixing",

            provider="ffmpeg",

            filename=master.filename,

            duration=master.duration,

        )

        asset = self.assets.register(
            asset
        )

        master.asset_id = asset.asset_id

        state.master_audio = master

        state.current_stage = "audio_mixing"

        state.status = "audio_complete"

        return state