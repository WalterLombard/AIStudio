"""
AIStudio Asset Models

Defines every production asset generated throughout the AIStudio
production pipeline.

Every file produced by AIStudio is represented by an AssetRecord and
tracked in the project AssetRegistry.

Author : AIStudio
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AssetRecord(BaseModel):
    """
    Represents a single production asset.
    """

    asset_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    asset_type: str = ""

    stage: str = ""

    provider: str = ""

    status: str = "completed"

    filename: str = ""

    relative_path: str = ""

    prompt: str = ""

    prompt_hash: str = ""

    source_scene: str = ""

    dependencies: list[str] = Field(
        default_factory=list
    )

    width: int = 0

    height: int = 0

    duration: float = 0.0

    fps: float = 0.0

    sample_rate: int = 0

    channels: int = 0

    file_size: int = 0

    checksum: str = ""

    version: int = 1

    created: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    modified: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @property
    def exists(
        self,
    ) -> bool:
        """
        Determine whether the asset file exists.
        """

        if not self.filename:

            return False

        return Path(
            self.filename
        ).exists()


class AssetRegistry(BaseModel):
    """
    Registry containing every generated asset for a project.
    """

    project_name: str = ""

    created: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    modified: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    assets: list[AssetRecord] = Field(
        default_factory=list
    )

    @property
    def total_assets(
        self,
    ) -> int:
        """
        Return the total number of registered assets.
        """

        return len(
            self.assets
        )

    def add(
        self,
        asset: AssetRecord,
    ) -> None:
        """
        Register a new asset.
        """

        asset.modified = datetime.now(
            UTC
        )

        self.assets.append(
            asset
        )

        self.modified = datetime.now(
            UTC
        )

    def get(
        self,
        asset_id: str,
    ) -> AssetRecord | None:
        """
        Retrieve an asset by its identifier.
        """

        for asset in self.assets:

            if asset.asset_id == asset_id:

                return asset

        return None

    def by_stage(
        self,
        stage: str,
    ) -> list[AssetRecord]:
        """
        Return all assets produced by a pipeline stage.
        """

        return [

            asset

            for asset in self.assets

            if asset.stage == stage

        ]

    def by_type(
        self,
        asset_type: str,
    ) -> list[AssetRecord]:
        """
        Return all assets of a given type.
        """

        return [

            asset

            for asset in self.assets

            if asset.asset_type == asset_type

        ]

    def remove(
        self,
        asset_id: str,
    ) -> bool:
        """
        Remove an asset from the registry.

        Returns
        -------
        bool
            True if the asset was removed.
        """

        original_count = len(
            self.assets
        )

        self.assets = [

            asset

            for asset in self.assets

            if asset.asset_id != asset_id

        ]

        removed = len(
            self.assets
        ) != original_count

        if removed:

            self.modified = datetime.now(
                UTC
            )

        return removed

    def clear(
        self,
    ) -> None:
        """
        Remove every asset from the registry.
        """

        self.assets.clear()

        self.modified = datetime.now(
            UTC
        )