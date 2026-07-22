"""
AIStudio Outline Models

Defines the documentary outline structure.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class OutlineScene(BaseModel):
    """
    Represents a single documentary scene within the outline.
    """

    scene: int | str = 1

    title: str = ""

    goal: str = ""

    duration: int = 0

    key_points: list[str] = Field(default_factory=list)

    visual_focus: str = ""

    emotional_tone: str = ""

    transition: str = ""


class OutlineData(BaseModel):
    """
    Complete documentary outline.
    """

    title: str = ""

    scene_count: int = 0

    total_duration: int = 0

    scenes: list[OutlineScene] = Field(default_factory=list)


class OutlineSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE outline scene.
    Supports flexible key names from LLM responses.
    """

    scene: Optional[OutlineScene] = None
    scenes: list[OutlineScene] = Field(default_factory=list)