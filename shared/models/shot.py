"""
AIStudio Shot Planning Models

Defines the cinematography production plan.

Produced by the Shot Planner.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ShotSpecification(BaseModel):
    """
    Complete cinematography specification for one storyboard shot.
    """

    scene_id: str = ""

    shot_number: int = 0

    visual_type: str = ""

    camera_height: str = ""

    camera_angle: str = ""

    lens: str = ""

    focal_length: str = ""

    framing: str = ""

    composition: str = ""

    depth_of_field: str = ""

    lighting: str = ""

    colour_palette: str = ""

    atmosphere: str = ""

    realism_level: str = ""

    environment: str = ""

    subject: str = ""

    continuity_notes: str = ""

    reference_images: list[str] = Field(
        default_factory=list
    )

    render_notes: str = ""


class ShotData(BaseModel):
    """
    Complete cinematography plan.
    """

    shots: list[ShotSpecification] = Field(
        default_factory=list
    )


class ShotSceneResponse(BaseModel):
    """
    Returned from one LLM call.
    """

    shot: ShotSpecification