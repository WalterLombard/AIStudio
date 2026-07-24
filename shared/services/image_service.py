"""
AIStudio Image Service

High-level interface used by the Image Generator Agent.

This service defines the public interface for image generation providers.
Concrete provider implementations (ComfyUI, Flux, SDXL, OpenAI, etc.)
will inherit or replace this implementation without affecting the rest
of AIStudio.

Author : AIStudio
"""

from __future__ import annotations

from shared.logger import get_logger
from shared.models import VisualAsset


LOGGER = get_logger("ImageService")


class ImageService:
    """
    High-level image generation service.
    """

    def __init__(self) -> None:
        """
        Initialise the image generation service.
        """

        LOGGER.info(
            "ImageService initialized."
        )

    def generate(
        self,
        asset: VisualAsset,
    ) -> VisualAsset:
        """
        Generate a single image from a planned visual asset.

        Parameters
        ----------
        asset
            Planned visual asset.

        Returns
        -------
        VisualAsset
            The generated visual asset.

        Raises
        ------
        NotImplementedError
            Raised until an image generation provider has been
            implemented.
        """

        raise NotImplementedError(
            "Image generation provider has not yet been implemented."
        )