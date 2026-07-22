"""
AIStudio Sound Effects Models

Defines the planning models and generated sound effect assets used by the
Sound Effects Generator.

These models represent the complete lifecycle of documentary sound effects,
from LLM planning through generated production assets.

Produced by the SFX Generator.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class SFXCue(BaseModel):
    """
    Defines the planned sound effect for a single storyboard shot.

    This model is produced by the LLM and represents the environmental
    ambience required for one approved shot.
    """

    scene_id: str = ""

    shot_number: int = 0

    image_asset_id: str = ""

    start_time: float = 0.0

    end_time: float = 0.0

    effect: str = ""

    description: str = ""

    intensity: float = 0.5

    notes: str = ""


class SFXData(BaseModel):
    """
    Complete documentary sound effects plan.

    Contains one sound effect cue for every approved shot.
    """

    cues: list[SFXCue] = Field(default_factory=list)


class SFXSceneResponse(BaseModel):
    """
    Expected JSON response from the LLM for sound effects planning.
    Supports both singular 'cue' and plural 'cues' payloads.
    """

    cue: Optional[SFXCue] = None
    cues: list[SFXCue] = Field(default_factory=list)


class SFXAsset(BaseModel):
    """
    Represents one generated sound effect asset.

    This model references the generated production asset after it has been
    created by the SFXService and registered with the AssetService.
    """

    asset_id: str = ""

    scene_id: str = ""

    shot_number: int = 0

    image_asset_id: str = ""

    provider: str = ""

    filename: str = ""

    duration: float = 0.0

    metadata: dict[str, object] = Field(default_factory=dict)


class SFXLibrary(BaseModel):
    """
    Collection of all generated documentary sound effects.

    This object is stored within ProjectState after the Sound Effects
    Generator completes successfully.
    """

    assets: list[SFXAsset] = Field(default_factory=list)