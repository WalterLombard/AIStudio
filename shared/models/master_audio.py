"""
AIStudio Master Audio Models

Defines the final mixed audio produced by the Audio Mixer.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel


class MasterAudioData(BaseModel):
    """
    Represents the final mastered soundtrack.
    """

    asset_id: str = ""

    filename: str = ""

    duration: float = 0.0

    sample_rate: int = 48000

    channels: int = 2

    loudness_lufs: float = -16.0