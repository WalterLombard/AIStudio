"""
AIStudio Image Models

Defines generated image assets.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImageAsset(BaseModel):
    """
    One generated image.
    """

    asset_id: str = ""

    prompt: str = ""

    provider: str = ""

    filename: str = ""

    width: int = 0

    height: int = 0


class ImageData(BaseModel):
    """
    Complete image library.
    """

    images: list[ImageAsset] = Field(default_factory=list)


class ImageSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE image.
    """

    image: ImageAsset