"""
AIStudio Script Models

Defines the documentary script produced by the Script Agent.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ScriptLine(BaseModel):
    """
    A single narration block within a documentary scene.
    """

    order: int | str = 1

    narration: str = ""

    visual_description: str = ""

    duration: float = 0.0


class ScriptScene(BaseModel):
    """
    One completed documentary scene.
    """

    scene: int | str = 1

    title: str = ""

    duration: float = 0.0

    lines: list[ScriptLine] = Field(default_factory=list)


class ScriptData(BaseModel):
    """
    Complete documentary script.
    """

    scenes: list[ScriptScene] = Field(default_factory=list)


class ScriptSceneResponse(BaseModel):
    """
    Returned by the LLM when generating script scenes.
    Supports both singular 'scene' and plural 'scenes' payloads.
    """

    scene: Optional[ScriptScene] = None
    scenes: list[ScriptScene] = Field(default_factory=list)