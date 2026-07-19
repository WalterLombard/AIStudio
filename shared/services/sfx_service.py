"""
AIStudio Sound Effects Service

Abstract sound effect generation service.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel


class SFXResult(BaseModel):

    filename: str

    duration: float

    provider: str

    metadata: dict


class SFXService:

    def __init__(self) -> None:

        self.output = Path("output/sfx")

        self.output.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(
        self,
        cue,
    ) -> SFXResult:

        filename = f"{uuid4()}.wav"

        file = self.output / filename

        file.touch()

        duration = cue.end_time - cue.start_time

        if duration <= 0:

            duration = 2.0

        return SFXResult(

            filename=str(file),

            duration=duration,

            provider="placeholder",

            metadata={

                "effect": cue.effect,

                "description": cue.description,

                "intensity": cue.intensity,

            },

        )