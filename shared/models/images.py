"""
AIStudio Image Models

Defines every generated image produced by the Image Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImageAsset(BaseModel):
    """
    One generated image.
    """

    scene: int = 0

    shot_number: int = 0

    asset_id: str = ""

    provider: str = ""

    prompt: str = ""

    negative_prompt: str = ""

    filename: str = ""

    width: int = 0

    height: int = 0

    seed: int = 0

    generation_time: float = 0.0

    status: str = "completed"


class ImageData(BaseModel):
    """
    Complete image library.
    """

    images: list[ImageAsset] = Field(
        default_factory=list,
    )


class ImageSceneResponse(BaseModel):
    """
    Returned by the LLM for one generated image.
    """

    image: ImageAsset