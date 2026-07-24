"""
AIStudio Audio Models

Defines the generated narration audio produced by the Voice Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AudioAsset(BaseModel):
    """
    One generated narration audio file.
    """

    scene: int = 0

    asset_id: str = ""

    provider: str = ""

    voice: str = ""

    filename: str = ""

    duration: float = 0.0

    sample_rate: int = 24000

    channels: int = 1

    status: str = "completed"


class AudioData(BaseModel):
    """
    Complete narration audio library.
    """

    assets: list[AudioAsset] = Field(
        default_factory=list,
    )

    total_duration: float = 0.0