"""
AIStudio Sound Effects Models

Defines sound effect planning and generated sound effect assets.

Produced by the SFX Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SFXCue(BaseModel):
    """
    One sound effect cue.
    """

    scene_id: str = ""

    start_time: float = 0.0

    end_time: float = 0.0

    effect: str = ""

    description: str = ""

    intensity: float = 0.5

    notes: str = ""


class SFXData(BaseModel):
    """
    Complete SFX plan.
    """

    cues: list[SFXCue] = Field(
        default_factory=list
    )


class SFXAsset(BaseModel):
    """
    One generated sound effect.
    """

    asset_id: str = ""

    scene_id: str = ""

    filename: str = ""

    duration: float = 0.0


class SFXLibrary(BaseModel):
    """
    Generated sound effects.
    """

    assets: list[SFXAsset] = Field(
        default_factory=list
    )