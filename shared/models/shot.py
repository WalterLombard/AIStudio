"""
AIStudio Shot Planning Models

Defines the render-ready cinematography plan produced by the
Shot Planner.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ShotSpecification(BaseModel):
    """
    Complete render specification for one shot.
    """

    scene: int = 0

    shot_number: int = 0

    duration: float = 0.0

    visual_type: str = ""

    subject: str = ""

    environment: str = ""

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

    image_prompt: str = ""

    negative_prompt: str = ""

    aspect_ratio: str = "16:9"

    width: int = 1920

    height: int = 1080

    seed: int = 0

    variations: int = 1

    continuity_notes: str = ""

    reference_images: list[str] = Field(
        default_factory=list,
    )

    render_notes: str = ""


class ShotData(BaseModel):
    """
    Complete cinematography plan.
    """

    shots: list[ShotSpecification] = Field(
        default_factory=list,
    )


class ShotSceneResponse(BaseModel):
    """
    Returned by one LLM call.
    """

    shot: ShotSpecification