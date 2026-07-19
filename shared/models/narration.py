"""
AIStudio Narration Models

Defines the narration performance plan.

This model is produced by the Narration Designer and consumed by the
Voice Generator.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NarrationSegment(BaseModel):
    """
    Performance instructions for one narration segment.
    """

    scene_id: str = ""

    start_time: float = 0.0

    end_time: float = 0.0

    text: str = ""

    emotion: str = ""

    speaking_rate: float = 1.0

    emphasis: list[str] = Field(
        default_factory=list
    )

    pause_before: float = 0.0

    pause_after: float = 0.0


class NarrationData(BaseModel):
    """
    Complete narration performance.
    """

    segments: list[NarrationSegment] = Field(
        default_factory=list
    )