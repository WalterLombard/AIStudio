"""
AIStudio Narration Models

Defines the narration performance plan produced by the Narration
Designer.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NarrationSegment(BaseModel):
    """
    Performance instructions for one documentary scene.
    """

    scene: int = 0

    start_time: float = 0.0

    end_time: float = 0.0

    duration: float = 0.0

    text: str = ""

    voice_style: str = ""

    emotion: str = ""

    speaking_rate: float = 1.0

    emphasis: list[str] = Field(
        default_factory=list,
    )

    pause_before: float = 0.0

    pause_after: float = 0.0


class NarrationData(BaseModel):
    """
    Complete narration plan.
    """

    segments: list[NarrationSegment] = Field(
        default_factory=list,
    )

    total_duration: float = 0.0


class NarrationSceneResponse(BaseModel):
    """
    Returned by the LLM for one narration segment.
    """

    segment: NarrationSegment