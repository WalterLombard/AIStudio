"""
AIStudio Research Section Models

Strongly typed responses returned by the Research Agent.

Each LLM call validates immediately before being merged into the
final ResearchData object.

Author : AIStudio
"""

from pydantic import BaseModel, Field

from .research import Misconception


class BackgroundResponse(BaseModel):

    executive_summary: str

    historical_background: str

    scientific_background: str


class FactsResponse(BaseModel):

    facts: list[str] = Field(default_factory=list)

    statistics: list[str] = Field(default_factory=list)

    timeline: list[str] = Field(default_factory=list)

    technical_terms: list[str] = Field(default_factory=list)


class MisconceptionsResponse(BaseModel):

    misconceptions: list[Misconception] = Field(default_factory=list)


class ProductionResponse(BaseModel):

    visual_opportunities: list[str] = Field(default_factory=list)

    broll_opportunities: list[str] = Field(default_factory=list)

    cinematic_moments: list[str] = Field(default_factory=list)

    emotional_beats: list[str] = Field(default_factory=list)

    narration_highlights: list[str] = Field(default_factory=list)


class ReferencesResponse(BaseModel):

    important_people: list[str] = Field(default_factory=list)

    important_locations: list[str] = Field(default_factory=list)

    search_keywords: list[str] = Field(default_factory=list)

    related_topics: list[str] = Field(default_factory=list)

    verification_notes: list[str] = Field(default_factory=list)