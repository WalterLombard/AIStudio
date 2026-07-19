"""
AIStudio Audio Models

Defines generated narration audio.

Produced by the Voice Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AudioAsset(BaseModel):
    """
    One generated narration file.
    """

    asset_id: str = ""

    scene_id: str = ""

    filename: str = ""

    duration: float = 0.0


class AudioData(BaseModel):
    """
    Generated narration audio.
    """

    assets: list[AudioAsset] = Field(
        default_factory=list
    )