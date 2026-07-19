"""
AIStudio Music Service

Abstract music generation service.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel


class MusicResult(BaseModel):

    filename: str

    duration: float

    provider: str

    metadata: dict


class MusicService:

    def __init__(self) -> None:

        self.output = Path("output/music")

        self.output.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        cue,
    ) -> MusicResult:

        filename = f"{uuid4()}.wav"

        file = self.output / filename

        file.touch()

        duration = cue.end_time - cue.start_time

        if duration <= 0:

            duration = 5.0

        return MusicResult(

            filename=str(file),

            duration=duration,

            provider="placeholder",

            metadata={

                "mood": cue.mood,

                "genre": cue.genre,

                "intensity": cue.intensity,

            },

        )