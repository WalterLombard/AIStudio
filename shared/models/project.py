"""
AIStudio Project Information

Stores metadata about the current documentary project.

Author : AIStudio
"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """
    Core metadata for a project instance.
    """

    project_name: str = ""

    title: str = ""

    topic: str = ""

    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    modified: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )