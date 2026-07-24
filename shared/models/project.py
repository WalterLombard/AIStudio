"""
AIStudio Project Information

Stores metadata about the current AIStudio documentary project.

This model contains project identity and filesystem metadata.
Pipeline execution state is maintained separately by ProjectState.

Author : AIStudio
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """
    Metadata describing an AIStudio project.
    """

    project_id: str = ""

    project_name: str = ""

    project_directory: str = ""

    title: str = ""

    topic: str = ""

    description: str = ""

    language: str = "English"

    created: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    modified: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    version: int = 1

    status: str = "created"