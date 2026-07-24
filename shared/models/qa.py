"""
AIStudio Quality Assurance Models

Defines the final quality assurance report produced by the QA Agent.

The QA report represents the final validation stage of the AIStudio
production pipeline and determines whether the completed documentary is
approved for release.

Produced by the QA Agent.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class QAIssue(BaseModel):
    """
    Represents a single quality assurance finding.
    """

    severity: str = ""

    stage: str = ""

    message: str = ""


class QAReport(BaseModel):
    """
    Represents the final quality assurance report.

    This report summarises the outcome of the production validation
    process and determines whether the documentary is approved for
    publication.
    """

    passed: bool = False

    issues: list[QAIssue] = Field(default_factory=list)

    metadata: dict[str, object] = Field(default_factory=dict)