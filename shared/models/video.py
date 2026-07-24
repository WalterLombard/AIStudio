"""
AIStudio Video Models

Defines the final rendered documentary produced by the Video Compiler.

This model represents the completed documentary after all visual and audio
assets have been compiled into a single production-ready video.

Produced by the Video Compiler.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VideoData(BaseModel):
    """
    Represents the final rendered documentary.

    This model is produced by the Video Compiler and becomes the primary
    deliverable of the AIStudio production pipeline.
    """

    asset_id: str = ""

    provider: str = ""

    filename: str = ""

    duration: float = 0.0

    width: int = 1920

    height: int = 1080

    fps: int = 30

    codec: str = "h264"

    bitrate: str = "12M"

    metadata: dict[str, object] = Field(default_factory=dict)