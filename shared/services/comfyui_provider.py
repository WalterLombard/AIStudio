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

from shared.models.images import ImageAsset


class ComfyUIProvider:
    """
    ComfyUI image provider contract.
    """

    def __init__(self) -> None:
        pass

    def generate(
        self,
        asset: ImageAsset,
    ) -> ImageAsset:
        """
        Generate an image asset via ComfyUI.

        Preserves contract interface while the ComfyUI backend is wired up.
        """
        asset.provider = "ComfyUI"
        return asset