"""
AIStudio Narration Models

Defines the narration performance plan.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NarrationSegment(BaseModel):
    """
    Performance instructions for one script scene.
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
    Complete narration plan.
    """

    segments: list[NarrationSegment] = Field(
        default_factory=list
    )


class NarrationSceneResponse(BaseModel):
    """
    Returned by the LLM when generating ONE narration segment.
    """

    segment: NarrationSegment