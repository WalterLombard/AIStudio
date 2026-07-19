"""
AIStudio Motion Models

Defines the cinematic camera movement for every storyboard scene.

The Motion Designer never creates video. It creates a production plan
that the Video Compiler later executes.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CameraMove(BaseModel):
    """
    Defines the camera movement for a single storyboard scene.
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
    Complete cinematic motion plan for the documentary.
    """

    scenes: list[CameraMove] = Field(
        default_factory=list
    )

    total_duration: float = 0.0