"""
AIStudio Storyboard Models

Defines the scene-by-scene storyboard structure.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class StoryboardShot(BaseModel):
    """
    A single shot within a storyboard scene.
    """

    shot_number: int | str = 1

    shot_type: str = ""

    camera_move: str = ""

    lens: str = ""

    framing: str = ""

    duration: float = 0.0

    prompt: str = ""

    narration: str = ""

    sound_effects: list[str] = Field(default_factory=list)

    notes: str = ""


class StoryboardScene(BaseModel):
    """
    A single scene composed of storyboard shots.
    """

    scene_number: int | str = 1

    title: str = ""

    shots: list[StoryboardShot] = Field(default_factory=list)


class StoryboardData(BaseModel):
    """
    Complete project storyboard.
    """

    scenes: list[StoryboardScene] = Field(default_factory=list)


class StoryboardSceneResponse(BaseModel):
    """
    Returned by the LLM when generating storyboard scenes.
    Supports both singular 'scene' and plural 'scenes' payloads.
    """

    scene: Optional[StoryboardScene] = None
    scenes: list[StoryboardScene] = Field(default_factory=list)