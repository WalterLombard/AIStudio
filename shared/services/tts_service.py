"""
AIStudio Text To Speech Service

Abstract interface used by the Voice Generator.

Initially this is a placeholder implementation.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel


class TTSResult(BaseModel):

    filename: str

    duration: float

    provider: str

    metadata: dict


class TTSService:

    def __init__(self) -> None:

        self.output = Path("output/audio")

        self.output.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate(

        self,

        text: str,

        emotion: str,

        speaking_rate: float,

        pause_before: float,

        pause_after: float,

    ) -> TTSResult:

        filename = f"{uuid4()}.wav"

        file = self.output / filename

        file.touch()

        estimated_duration = max(

            len(text.split()) / 2.6,

            1.0,

        )

        return TTSResult(

            filename=str(file),

            duration=estimated_duration,

            provider="placeholder",

            metadata={

                "emotion": emotion,

                "speaking_rate": speaking_rate,

                "pause_before": pause_before,

                "pause_after": pause_after,

            },

        )