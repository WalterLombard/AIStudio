"""
AIStudio QA Report Models

Defines automated QA inspection reports and flags.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class QAIssue(BaseModel):
    """
    Individual issue or warning identified by QA inspection.
    """

    severity: str = ""

    message: str = ""

    stage: str = ""


class QAReport(BaseModel):
    """
    Aggregated QA validation report.
    """

    passed: bool = False

    issues: list[QAIssue] = Field(default_factory=list)