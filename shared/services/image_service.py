"""
AIStudio Image Service

Provides a unified interface for generating images regardless of the
underlying provider.

The Image Generator Agent never communicates directly with ComfyUI,
Flux, SDXL or OpenAI. It always calls this service.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    VisualAsset,
)

from shared.providers.image_provider import (
    ImageProvider,
)


class ImageService:
    """
    High-level image generation service.
    """

    def __init__(self) -> None:

        self.provider = ImageProvider()

    def generate_image(
        self,
        asset: VisualAsset,
    ) -> VisualAsset:
        """
        Generate one image from a VisualAsset.

        Parameters
        ----------
        asset
            Planned visual asset.

        Returns
        -------
        Updated VisualAsset
        """

        return self.provider.generate(asset)