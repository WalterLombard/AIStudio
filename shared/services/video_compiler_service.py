"""
AIStudio Video Compiler Service

Compiles the documentary into a final MP4.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from shared.models import (
    ImageData,
    MasterAudioData,
    MotionData,
    VideoData,
)


class VideoCompilerService:

    def __init__(self) -> None:

        self.output = Path("output/video")

        self.output.mkdir(
            parents=True,
            exist_ok=True,
        )

    def compile(

        self,

        images: ImageData,

        motion: MotionData,

        audio: MasterAudioData,

    ) -> VideoData:

        output = self.output / f"{uuid4()}.mp4"

        output.touch()

        #
        # FFmpeg render implementation
        # will be added here.
        #

        return VideoData(

            filename=str(output),

            duration=audio.duration,

        )