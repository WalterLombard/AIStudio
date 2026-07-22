"""
AIStudio Image Service

High-level interface used by the Image Generator Agent.

Author : AIStudio
"""

from __future__ import annotations

import logging
from typing import Any

from shared.models.images import ImageAsset

LOGGER = logging.getLogger("ImageService")


class ImageService:
    """
    High-level image generation service.
    """

    def __init__(self) -> None:
        LOGGER.info("ImageService initialized.")

    def generate_image(
        self,
        spec: Any,
    ) -> ImageAsset:
        """
        Generate one image asset.

        Parameters
        ----------
        spec
            Planned shot specification or visual asset prompt.

        Returns
        -------
        ImageAsset
        """
        raise NotImplementedError(
            "Image generation provider has not yet been implemented."
        )