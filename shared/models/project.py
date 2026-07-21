"""
AIStudio Project Information

Stores metadata about the current documentary project.

Author : AIStudio
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProjectInfo(BaseModel):

    project_name: str = ""

    title: str = ""

    topic: str = ""

    created: datetime = datetime.now()

    modified: datetime = datetime.now()