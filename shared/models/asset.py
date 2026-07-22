"""
AIStudio Asset Models

Defines every production asset produced by AIStudio.

Every generated file becomes an AssetRecord.

Author : AIStudio
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class AssetRecord(BaseModel):
    """
    Represents one generated production asset.
    """

    asset_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    asset_type: str = ""

    stage: str = ""

    provider: str = ""

    filename: str = ""

    prompt: str = ""

    source_scene: str = ""

    width: int = 0

    height: int = 0

    duration: float = 0.0

    checksum: str = ""

    version: int = 1

    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict = Field(
        default_factory=dict
    )


class AssetRegistry(BaseModel):
    """
    Registry containing every project asset.
    """

    assets: list[AssetRecord] = Field(
        default_factory=list
    )