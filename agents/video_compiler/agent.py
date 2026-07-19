"""
AIStudio Video Compiler Agent

Creates the finished documentary.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    AssetRecord,
    ProjectState,
)

from shared.services import (
    AssetService,
    VideoCompilerService,
)


class VideoCompilerAgent:

    def __init__(self) -> None:

        self.compiler = VideoCompilerService()

        self.assets = AssetService()

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.images is None:

            raise ValueError(
                "Images have not been generated."
            )

        if state.motion is None:

            raise ValueError(
                "Motion plan missing."
            )

        if state.master_audio is None:

            raise ValueError(
                "Master audio missing."
            )

        video = self.compiler.compile(

            images=state.images,

            motion=state.motion,

            audio=state.master_audio,

        )

        asset = AssetRecord(

            asset_type="video",

            stage="video_compile",

            provider="ffmpeg",

            filename=video.filename,

            duration=video.duration,

        )

        asset = self.assets.register(
            asset
        )

        video.asset_id = asset.asset_id

        state.video = video

        state.current_stage = "video_compile"

        state.status = "video_complete"

        return state