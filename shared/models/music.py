"""
AIStudio Music Models

Defines background music planning and generated music assets.

Produced by the Music Generator.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class MusicCue(BaseModel):
    """
    One music cue for one storyboard shot.
    """

    scene_id: str = ""

    shot_number: int = 0

    image_asset_id: str = ""

    start_time: float = 0.0

    end_time: float = 0.0

    mood: str = ""

    intensity: float = 0.5

    genre: str = ""

    notes: str = ""


class MusicData(BaseModel):
    """
    Complete music plan.
    """

    cues: list[MusicCue] = Field(default_factory=list)


class MusicSceneResponse(BaseModel):
    """
    Returned by the LLM when generating music cues.
    Supports both plural 'cues' array and singular 'cue' payload.
    """

    cues: list[MusicCue] = Field(default_factory=list)
    cue: Optional[MusicCue] = None


class MusicAsset(BaseModel):
    """
    Generated music file.
    """

    asset_id: str = ""

    scene_id: str = ""

    shot_number: int = 0

    image_asset_id: str = ""

    filename: str = ""

    duration: float = 0.0


class MusicLibrary(BaseModel):
    """
    Generated music assets.
    """

    assets: list[MusicAsset] = Field(default_factory=list)