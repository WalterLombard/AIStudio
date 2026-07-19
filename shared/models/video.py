"""
AIStudio Video Models

Defines the final rendered documentary.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel


class VideoData(BaseModel):
    """
    Final rendered documentary.
    """

    asset_id: str = ""

    filename: str = ""

    duration: float = 0.0

    width: int = 1920

    height: int = 1080

    fps: int = 30

    codec: str = "h264"

    bitrate: str = "12M"