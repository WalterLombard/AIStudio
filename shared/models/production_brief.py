"""
AIStudio Production Brief Model

Defines the strategic creative direction and metadata for a documentary project.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProductionBrief(BaseModel):
    """
    Core creative brief for documentary production.
    """

    title: str = ""

    topic: str = ""

    audience: str = ""

    duration_minutes: int = 10

    tone: str = ""

    style: str = ""

    visual_style: str = ""

    music_style: str = ""

    production_notes: str = ""

    story_arc: str = ""

    viewer_hook: str = ""

    central_question: str = ""

    ending_payoff: str = ""

    target_emotion: str = ""

    narrative_structure: str = ""

    retention_strategy: str = ""

    thumbnail_idea: str = ""

    title_variations: list[str] = Field(default_factory=list)