"""
AIStudio Audio Mixer Service

Combines narration, music and sound effects into a single mastered
audio track.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from shared.models import (
    AudioData,
    MasterAudioData,
    MusicLibrary,
    SFXLibrary,
)


class AudioMixerService:
    """
    High-level audio mixing service.
    """

    def __init__(self) -> None:
        self.output = Path("output/master_audio")
        self.output.mkdir(
            parents=True,
            exist_ok=True,
        )

    def mix(
        self,
        narration: AudioData | None = None,
        music: MusicLibrary | None = None,
        sfx: SFXLibrary | None = None,
    ) -> MasterAudioData:
        """
        Produce the final mastered audio track.

        FFmpeg integration will be implemented in runtime execution.
        """
        output_file = self.output / f"{uuid4()}.wav"
        output_file.touch()

        # Compute combined audio duration from available streams
        total_duration = 0.0
        if narration and hasattr(narration, "assets"):
            total_duration = sum(getattr(a, "duration", 0.0) for a in narration.assets)

        return MasterAudioData(
            filename=str(output_file),
            duration=total_duration,
        )