"""
AIStudio Sound Effects Models

Defines the planning models and generated sound effect assets used by
the Sound Effects Generator.

Produced by the SFX Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SFXCue(BaseModel):
    """
    Planned sound effect for one documentary scene.
    """

    scene: int = 0

    shot_number: int = 0

    image_asset_id: str = ""

    start_time: float = 0.0

    end_time: float = 0.0

    duration: float = 0.0

    effect: str = ""

    description: str = ""

    intensity: float = 0.5

    notes: str = ""


class SFXData(BaseModel):
    """
    Complete documentary sound effects plan.
    """

    cues: list[SFXCue] = Field(
        default_factory=list,
    )

    total_duration: float = 0.0


class SFXSceneResponse(BaseModel):
    """
    Returned by the LLM for one sound effect cue.
    """

    cue: SFXCue


class SFXAsset(BaseModel):
    """
    One generated sound effect asset.
    """

    asset_id: str = ""

    scene: int = 0

    shot_number: int = 0

    image_asset_id: str = ""

    provider: str = ""

    filename: str = ""

    duration: float = 0.0

    sample_rate: int = 44100

    channels: int = 2

    status: str = "completed"

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )


class SFXLibrary(BaseModel):
    """
    Generated sound effect library.
    """

    assets: list[SFXAsset] = Field(
        default_factory=list,
    )

    total_duration: float = 0.0