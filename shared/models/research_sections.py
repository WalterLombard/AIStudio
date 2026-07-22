"""
AIStudio Research Section Models

Strongly typed responses returned by the Research Agent.

Each LLM call validates immediately before being merged into the
final ResearchData object.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .research import Misconception


class BackgroundResponse(BaseModel):
    """
    Structured response model for high-level background research.
    """

    executive_summary: str = ""

    historical_background: str = ""

    scientific_background: str = ""


class FactsResponse(BaseModel):
    """
    Structured response model for hard facts and timeline metadata.
    """

    facts: list[str] = Field(default_factory=list)

    statistics: list[str] = Field(default_factory=list)

    timeline: list[str] = Field(default_factory=list)

    technical_terms: list[str] = Field(default_factory=list)


class MisconceptionsResponse(BaseModel):
    """
    Structured response model for identified common myths and corrections.
    """

    misconceptions: list[Misconception] = Field(default_factory=list)


class ProductionResponse(BaseModel):
    """
    Structured response model for visual direction and narrative opportunities.
    """

    visual_opportunities: list[str] = Field(default_factory=list)

    broll_opportunities: list[str] = Field(default_factory=list)

    cinematic_moments: list[str] = Field(default_factory=list)

    emotional_beats: list[str] = Field(default_factory=list)

    narration_highlights: list[str] = Field(default_factory=list)


class ReferencesResponse(BaseModel):
    """
    Structured response model for entity references and topics.
    """

    important_people: list[str] = Field(default_factory=list)

    important_locations: list[str] = Field(default_factory=list)

    search_keywords: list[str] = Field(default_factory=list)

    related_topics: list[str] = Field(default_factory=list)

    verification_notes: list[str] = Field(default_factory=list)