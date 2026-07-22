"""
AIStudio Audio Mixer Agent

Produces the final mastered soundtrack by combining narration, background
music, and sound effects through AudioMixerService or audio FastMCP server.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import (
    AssetRecord,
    ProjectState,
)
from shared.services import (
    AssetService,
    AudioMixerService,
)

# Optional import of FastMCP audio server tool
try:
    from servers.audio_server import mix_master_soundtrack
except ImportError:
    mix_master_soundtrack = None

LOGGER = logging.getLogger("AudioMixerAgent")


class AudioMixerAgent:
    """
    Combines narration, background music, and sound effects into a broadcast-ready master audio track.
    """

    def __init__(self) -> None:
        self.assets = AssetService()
        self.mixer = AudioMixerService()

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.audio is None:
            raise ValueError(
                "AudioMixerAgent failure: Narration audio (state.audio) must exist before mixing."
            )
        if state.music is None or not getattr(state.music, "assets", None):
            raise ValueError(
                "AudioMixerAgent failure: Music assets (state.music) must exist before mixing."
            )
        if state.sfx is None or not getattr(state.sfx, "assets", None):
            raise ValueError(
                "AudioMixerAgent failure: Sound effects (state.sfx) must exist before mixing."
            )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the audio mixing pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Audio Mixer Agent")

        try:
            if mix_master_soundtrack:
                LOGGER.info("Executing audio mix via FastMCP audio server...")
                master = mix_master_soundtrack(
                    narration=state.audio,
                    music=state.music,
                    sfx=state.sfx,
                )
            else:
                LOGGER.info("Executing audio mix via AudioMixerService...")
                master = self.mixer.mix(
                    narration=state.audio,
                    music=state.music,
                    sfx=state.sfx,
                )
        except Exception as err:
            raise RuntimeError(
                f"AudioMixerAgent failure during mix stage: {err}"
            ) from err

        # Register master audio asset
        asset = AssetRecord(
            asset_type="master_audio",
            stage="audio_mixing",
            provider="ffmpeg",
            filename=getattr(master, "filename", str(master)),
            duration=getattr(master, "duration", 0.0),
        )

        registered_asset = self.assets.register(asset)
        if hasattr(master, "asset_id"):
            master.asset_id = registered_asset.asset_id

        state.master_audio = master
        state.current_stage = "audio_mixing"
        state.status = "audio_complete"

        LOGGER.info("Audio Mixer Agent completed successfully.")

        return state