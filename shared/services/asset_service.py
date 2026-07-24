"""
AIStudio Asset Service

Responsible for managing every generated production asset.

This service provides the central registry for all production assets
generated throughout the AIStudio pipeline.

Author : AIStudio
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from shared.logger import get_logger
from shared.models import (
    AssetRecord,
    AssetRegistry,
)


LOGGER = get_logger("AssetService")


class AssetService:
    """
    Central asset registry.
    """

    REGISTRY_DIRECTORY = "registry"

    REGISTRY_FILENAME = "assets.json"

    def __init__(
        self,
        project_directory: str = ".",
    ) -> None:
        """
        Initialise the asset registry.
        """

        self.registry_path = (
            Path(project_directory)
            / self.REGISTRY_DIRECTORY
            / self.REGISTRY_FILENAME
        )

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.registry = self._load_registry()

    def _load_registry(
        self,
    ) -> AssetRegistry:
        """
        Load the asset registry from disk.
        """

        if self.registry_path.exists():

            LOGGER.info(
                "Loading asset registry: %s",
                self.registry_path,
            )

            return AssetRegistry.model_validate_json(
                self.registry_path.read_text(
                    encoding="utf-8",
                )
            )

        LOGGER.info(
            "Creating new asset registry."
        )

        registry = AssetRegistry()

        self._save_registry(
            registry,
        )

        return registry

    def _save_registry(
        self,
        registry: AssetRegistry,
    ) -> None:
        """
        Save an asset registry to disk.
        """

        registry.modified = datetime.now(
            UTC,
        )

        self.registry_path.write_text(
            registry.model_dump_json(
                indent=4,
            ),
            encoding="utf-8",
        )

    def save(
        self,
    ) -> None:
        """
        Persist the current registry.
        """

        self._save_registry(
            self.registry,
        )

    def register(
        self,
        asset: AssetRecord,
    ) -> AssetRecord:
        """
        Register a newly generated asset.
        """

        asset.modified = datetime.now(
            UTC,
        )

        self.registry.assets.append(
            asset,
        )

        self.save()

        LOGGER.info(
            "Registered asset %s (%s)",
            asset.asset_id,
            asset.asset_type,
        )

        return asset

    def get_asset(
        self,
        asset_id: str,
    ) -> AssetRecord | None:
        """
        Retrieve an asset by identifier.
        """

        return self.registry.get(
            asset_id,
        )

    def get_assets_by_stage(
        self,
        stage: str,
    ) -> list[AssetRecord]:
        """
        Retrieve every asset belonging to a stage.
        """

        return self.registry.by_stage(
            stage,
        )

    def get_assets_by_type(
        self,
        asset_type: str,
    ) -> list[AssetRecord]:
        """
        Retrieve every asset of a given type.
        """

        return self.registry.by_type(
            asset_type,
        )

    def update(
        self,
        asset: AssetRecord,
    ) -> None:
        """
        Update an existing asset.
        """

        asset.modified = datetime.now(
            UTC,
        )

        for index, existing in enumerate(
            self.registry.assets,
        ):

            if existing.asset_id == asset.asset_id:

                self.registry.assets[index] = asset

                self.save()

                LOGGER.info(
                    "Updated asset %s",
                    asset.asset_id,
                )

                return

        raise ValueError(
            f"Unknown asset '{asset.asset_id}'."
        )

    def remove(
        self,
        asset_id: str,
    ) -> None:
        """
        Remove an asset from the registry.
        """

        self.registry.assets = [

            asset

            for asset in self.registry.assets

            if asset.asset_id != asset_id

        ]

        self.save()

        LOGGER.info(
            "Removed asset %s",
            asset_id,
        )

    def asset_exists(
        self,
        asset_id: str,
    ) -> bool:
        """
        Determine whether an asset exists.
        """

        return self.get_asset(
            asset_id,
        ) is not None

    def clear(
        self,
    ) -> None:
        """
        Remove all registered assets.
        """

        self.registry.assets.clear()

        self.save()

        LOGGER.info(
            "Asset registry cleared."
        )

    @property
    def total_assets(
        self,
    ) -> int:
        """
        Return the number of registered assets.
        """

        return self.registry.total_assets