"""
AIStudio Audio Mixer Agent

Produces the final mastered documentary soundtrack.

The Audio Mixer combines the approved narration, music and sound effects
into a single production-ready master audio asset suitable for video
compilation.

Produced by the Audio Department.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    AssetRecord,
    MasterAudioData,
    ProjectState,
)

from shared.services import (
    AssetService,
    AudioMixerService,
)


class AudioMixerAgent:
    """
    Produces the final mastered documentary soundtrack.
    """

    def __init__(self) -> None:
        """
        Initialise required services.
        """

        self.assets = AssetService()

        self.mixer = AudioMixerService()

    def _validate_state(
        self,
        state: ProjectState,
    ) -> None:
        """
        Validate required upstream state.
        """

        if state.audio is None:
            raise ValueError(
                "Narration audio must exist before AudioMixerAgent runs."
            )

        if state.music is None:
            raise ValueError(
                "MusicLibrary must exist before AudioMixerAgent runs."
            )

        if state.sfx is None:
            raise ValueError(
                "SFXLibrary must exist before AudioMixerAgent runs."
            )

    def _mix_audio(
        self,
        state: ProjectState,
    ) -> MasterAudioData:
        """
        Produce the mastered soundtrack.
        """

        return self.mixer.mix(
            narration=state.audio,
            music=state.music,
            sfx=state.sfx,
        )

    def _register_asset(
        self,
        master: MasterAudioData,
    ) -> MasterAudioData:
        """
        Register the mastered soundtrack.
        """

        asset_record = AssetRecord(
            asset_type="master_audio",
            stage="audio_mixing",
            provider=master.provider,
            filename=master.filename,
            duration=master.duration,
            metadata=master.metadata,
        )

        registered = self.assets.register(
            asset_record,
        )

        master.asset_id = registered.asset_id

        return master

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Execute the Audio Mixer.
        """

        self._validate_state(
            state,
        )

        master = self._mix_audio(
            state,
        )

        state.master_audio = self._register_asset(
            master,
        )

        state.current_stage = "audio_mixing"

        state.status = "audio_complete"

        return state