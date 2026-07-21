"""
AIStudio ComfyUI Provider

Implements image generation using ComfyUI.

Initially this provider is only responsible for establishing the
contract with the rest of AIStudio.

Actual workflow execution will be implemented after the production
pipeline is complete.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    VisualAsset,
)


class ComfyUIProvider:
    """
    ComfyUI image provider.
    """

    def __init__(self) -> None:

        pass

    def generate(
        self,
        asset: VisualAsset,
    ) -> VisualAsset:
        """
        Generate an image.

        Currently this is a placeholder implementation that preserves
        the interface while the ComfyUI backend is developed.
        """

        asset.provider = "ComfyUI"

        return asset