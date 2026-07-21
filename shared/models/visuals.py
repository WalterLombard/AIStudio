"""
AIStudio Visual Models

Defines all visual assets produced by the Visual Planner.

Author : AIStudio
"""

from pydantic import BaseModel, Field


class VisualAsset(BaseModel):
    """
    A single visual asset generated for one storyboard scene.
    """

    asset_id: str = ""

    prompt: str = ""

    asset_type: str = ""

    provider: str = ""

    filename: str = ""

    width: int = 0

    height: int = 0

    duration: float = 0.0

    metadata: dict = Field(default_factory=dict)


class VisualData(BaseModel):
    """
    Complete visual production plan.
    """

    assets: list[VisualAsset] = Field(default_factory=list)


class VisualSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE storyboard scene's
    visual asset.
    """

    asset: VisualAsset