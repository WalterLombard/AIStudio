"""
AIStudio Motion Models

Defines the cinematic camera movement for every generated image.

Author : AIStudio
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class CameraMove(BaseModel):
    """
    Camera movement for one generated image.
    """

    scene_id: str = ""

    image_asset_id: str = ""

    narration_start: float = 0.0

    narration_end: float = 0.0

    duration: float = 0.0

    movement: str = ""

    easing: str = "ease_in_out"

    zoom_start: float = 1.0

    zoom_end: float = 1.0

    pan_x: float = 0.0

    pan_y: float = 0.0

    rotation: float = 0.0

    transition_in: str = "cut"

    transition_out: str = "cut"

    notes: str = ""


class MotionData(BaseModel):
    """
    Complete motion plan.
    """

    scenes: list[CameraMove] = Field(
        default_factory=list
    )

    total_duration: float = 0.0


class MotionSceneResponse(BaseModel):
    """
    Returned by the LLM when generating camera moves.
    Supports both plural 'scenes' array and singular 'scene' payload.
    """

    scenes: list[CameraMove] = Field(default_factory=list)
    scene: Optional[CameraMove] = None