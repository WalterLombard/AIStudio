"""
AIStudio Image Generator Agent

Generates every AI image required for the documentary.

Every generated image is immediately registered with the
Asset Service.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import (
    AssetRecord,
    ImageAsset,
    ImageData,
    ProjectState,
)

from shared.services import (
    AssetService,
    ImageService,
)

LOGGER = logging.getLogger("ImageGeneratorAgent")


class ImageGeneratorAgent:
    """
    Generates all storyboard images.
    """

    def __init__(self) -> None:

        self.image_service = ImageService()

        self.asset_service = AssetService()

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.visuals is None:

            raise ValueError(
                "VisualData must exist before image generation."
            )

        LOGGER.info(
            "Starting Image Generation..."
        )

        image_library = ImageData()

        for visual in state.visuals.assets:

            generated = self.image_service.generate_image(
                visual
            )

            asset = AssetRecord(

                asset_type="image",

                stage="image_generation",

                provider=generated.provider,

                filename=generated.filename,

                prompt=generated.prompt,

                source_scene=generated.asset_id,

                width=generated.width,

                height=generated.height,

                metadata=generated.metadata,

            )

            asset = self.asset_service.register(
                asset
            )

            image_library.assets.append(

                ImageAsset(

                    asset_id=asset.asset_id,

                    filename=asset.filename,

                    prompt=asset.prompt,

                    provider=asset.provider,

                    width=asset.width,

                    height=asset.height,

                    metadata=asset.metadata,

                )

            )

        state.images = image_library

        state.current_stage = "image_generation"

        state.status = "images_complete"

        LOGGER.info(
            "Image Generation Complete."
        )

        return state