"""
AIStudio Master Audio Models

Defines the final mastered soundtrack produced by the Audio Mixer.

This model represents the completed documentary soundtrack after narration,
music and sound effects have been mixed into a single production-ready audio
asset.

Produced by the Audio Mixer.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MasterAudioData(BaseModel):
    """
    Represents the final mastered documentary soundtrack.

    This model is produced by the Audio Mixer and becomes the audio source
    consumed by the Video Compiler.
    """

    asset_id: str = ""

    provider: str = ""

    filename: str = ""

    duration: float = 0.0

    sample_rate: int = 48_000

    channels: int = 2

    loudness_lufs: float = -16.0

    metadata: dict[str, object] = Field(default_factory=dict)