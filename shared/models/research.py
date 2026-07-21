"""
AIStudio Research Models

Defines all research information gathered for the documentary.

Author : AIStudio
"""

from pydantic import BaseModel, Field


class Misconception(BaseModel):
    """
    A common misconception and its factual correction.
    """

    myth: str

    reality: str


class ResearchData(BaseModel):
    """
    Complete research package used by downstream agents.
    """

    executive_summary: str = ""

    historical_background: str = ""

    scientific_background: str = ""

    facts: list[str] = Field(default_factory=list)

    statistics: list[str] = Field(default_factory=list)

    timeline: list[str] = Field(default_factory=list)

    technical_terms: list[str] = Field(default_factory=list)

    misconceptions: list[Misconception] = Field(default_factory=list)

    visual_opportunities: list[str] = Field(default_factory=list)

    broll_opportunities: list[str] = Field(default_factory=list)

    cinematic_moments: list[str] = Field(default_factory=list)

    emotional_beats: list[str] = Field(default_factory=list)

    narration_highlights: list[str] = Field(default_factory=list)

    important_people: list[str] = Field(default_factory=list)

    important_locations: list[str] = Field(default_factory=list)

    search_keywords: list[str] = Field(default_factory=list)

    related_topics: list[str] = Field(default_factory=list)

    verification_notes: list[str] = Field(default_factory=list)