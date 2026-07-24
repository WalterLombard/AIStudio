"""
AIStudio Video Compiler Agent

Produces the final rendered documentary.

The Video Compiler assembles the approved visual and audio assets into a
single production-ready documentary suitable for quality assurance and
distribution.

Produced by the Video Production department.

Author : AIStudio
"""

from __future__ import annotations

from shared.models import (
    AssetRecord,
    ProjectState,
    VideoData,
)

from shared.services import (
    AssetService,
    VideoCompilerService,
)


class VideoCompilerAgent:
    """
    Produces the final rendered documentary.
    """

    def __init__(self) -> None:
        """
        Initialise required services.
        """

        self.compiler = VideoCompilerService()

        self.assets = AssetService()

    def _validate_state(
        self,
        state: ProjectState,
    ) -> None:
        """
        Validate required upstream state.
        """

        if state.images is None:
            raise ValueError(
                "ImageData must exist before VideoCompilerAgent runs."
            )

        if state.motion is None:
            raise ValueError(
                "MotionData must exist before VideoCompilerAgent runs."
            )

        if state.master_audio is None:
            raise ValueError(
                "MasterAudioData must exist before VideoCompilerAgent runs."
            )

    def _compile_video(
        self,
        state: ProjectState,
    ) -> VideoData:
        """
        Compile the final documentary.
        """

        return self.compiler.compile(
            images=state.images,
            motion=state.motion,
            audio=state.master_audio,
        )

    def _register_asset(
        self,
        video: VideoData,
    ) -> VideoData:
        """
        Register the rendered documentary.
        """

        asset_record = AssetRecord(
            asset_type="video",
            stage="video_compile",
            provider=video.provider,
            filename=video.filename,
            duration=video.duration,
            metadata=video.metadata,
        )

        registered = self.assets.register(
            asset_record,
        )

        video.asset_id = registered.asset_id

        return video

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Execute the Video Compiler.
        """

        self._validate_state(
            state,
        )

        video = self._compile_video(
            state,
        )

        state.video = self._register_asset(
            video,
        )

        state.current_stage = "video_compile"

        state.status = "video_complete"

        return state