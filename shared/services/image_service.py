"""
AIStudio Image Service

High-level interface used by the Image Generator Agent.

This service owns the image-generation workflow.

Provider implementations (ComfyUI, Flux, SDXL, OpenAI, etc.) are
introduced later. Until then this service defines the public API that
the rest of AIStudio depends upon.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import (
    VisualAsset,
)

LOGGER = logging.getLogger("ImageService")


class ImageService:
    """
    High-level image generation service.
    """

    def __init__(self) -> None:

        LOGGER.info(
            "ImageService initialized."
        )

    def generate_image(
        self,
        asset: VisualAsset,
    ) -> VisualAsset:
        """
        Generate one image.

        This functionality will be implemented once the provider layer
        is introduced.

        Parameters
        ----------
        asset
            Planned visual asset.

        Returns
        -------
        VisualAsset
        """

        raise NotImplementedError(
            "Image generation provider has not yet been implemented."
        )