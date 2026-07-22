"""
AIStudio Asset Service

Responsible for managing every generated production asset.

This service acts as the central registry for images, audio,
motion, video and future assets.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path

from shared.models.asset import (
    AssetRecord,
    AssetRegistry,
)


class AssetService:
    """
    Central asset registry.
    """

    def __init__(
        self,
        project_directory: str = ".",
    ) -> None:
        self.registry_path = (
            Path(project_directory)
            / "registry"
            / "assets.json"
        )

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self.registry_path.exists():
            self.registry = AssetRegistry.model_validate_json(
                self.registry_path.read_text(
                    encoding="utf-8"
                )
            )
        else:
            self.registry = AssetRegistry()
            self.save()

    def save(self) -> None:
        """
        Save registry to disk.
        """
        self.registry_path.write_text(
            self.registry.model_dump_json(
                indent=4
            ),
            encoding="utf-8",
        )

    def register(
        self,
        asset: AssetRecord,
    ) -> AssetRecord:
        """
        Register a newly generated asset.
        """
        self.registry.assets.append(
            asset
        )
        self.save()
        return asset

    def get_asset(
        self,
        asset_id: str,
    ) -> AssetRecord | None:
        """
        Retrieve an asset by ID.
        """
        for asset in self.registry.assets:
            if asset.asset_id == asset_id:
                return asset
        return None

    def get_assets_by_stage(
        self,
        stage: str,
    ) -> list[AssetRecord]:
        """
        Return every asset belonging to a stage.
        """
        return [
            asset
            for asset in self.registry.assets
            if asset.stage == stage
        ]

    def get_assets_by_type(
        self,
        asset_type: str,
    ) -> list[AssetRecord]:
        """
        Return every asset of a given type.
        """
        return [
            asset
            for asset in self.registry.assets
            if asset.asset_type == asset_type
        ]

    def update(
        self,
        asset: AssetRecord,
    ) -> None:
        """
        Update an existing asset.
        """
        for index, existing in enumerate(
            self.registry.assets
        ):
            if existing.asset_id == asset.asset_id:
                self.registry.assets[index] = asset
                self.save()
                return

        raise ValueError(
            f"Unknown asset '{asset.asset_id}'"
        )

    def remove(
        self,
        asset_id: str,
    ) -> None:
        """
        Remove an asset.
        """
        self.registry.assets = [
            asset
            for asset in self.registry.assets
            if asset.asset_id != asset_id
        ]
        self.save()