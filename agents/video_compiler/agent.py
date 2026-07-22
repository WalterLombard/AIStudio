"""
AIStudio Video Compiler Agent

Creates the finished documentary by combining generated images, motion plans,
and mastered audio using VideoCompilerService / compiler_server FastMCP tool.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import (
    AssetRecord,
    ProjectState,
)
from shared.services import (
    AssetService,
    VideoCompilerService,
)

# Import FastMCP compiler server entrypoint if available
try:
    from servers.compiler_server import assemble_final_video
except ImportError:
    assemble_final_video = None

LOGGER = logging.getLogger("VideoCompilerAgent")


class VideoCompilerAgent:
    """
    Assembles and renders the final 1080p documentary MP4 from production assets.
    """

    def __init__(self) -> None:
        self.compiler = VideoCompilerService()
        self.assets = AssetService()

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.images is None or not getattr(state.images, "images", None):
            raise ValueError(
                "VideoCompilerAgent failure: Generated images (state.images) missing before video compilation."
            )
        if state.motion is None or not getattr(state.motion, "scenes", None):
            raise ValueError(
                "VideoCompilerAgent failure: Motion plan (state.motion) missing before video compilation."
            )
        if state.master_audio is None:
            raise ValueError(
                "VideoCompilerAgent failure: Master audio track (state.master_audio) missing before video compilation."
            )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Executes the video compilation and rendering pipeline step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Video Compiler Agent")

        try:
            # Prefer FastMCP compiler server if function is imported
            if assemble_final_video:
                LOGGER.info("Invoking compiler_server for final video assembly...")
                video = assemble_final_video(
                    images=state.images,
                    motion=state.motion,
                    audio=state.master_audio,
                )
            else:
                LOGGER.info("Fallback: Invoking VideoCompilerService for final video assembly...")
                video = self.compiler.compile(
                    images=state.images,
                    motion=state.motion,
                    audio=state.master_audio,
                )
        except Exception as err:
            raise RuntimeError(
                f"VideoCompilerAgent failure during rendering stage: {err}"
            ) from err

        # Register output in asset management
        asset = AssetRecord(
            asset_type="video",
            stage="video_compile",
            provider="ffmpeg",
            filename=getattr(video, "filename", "output.mp4"),
            duration=getattr(video, "duration", 0.0),
        )

        registered_asset = self.assets.register(asset)
        if hasattr(video, "asset_id"):
            video.asset_id = registered_asset.asset_id

        # Update ProjectState metadata
        state.video = video
        if hasattr(state, "final_video_path"):
            state.final_video_path = getattr(video, "filename", str(video))

        state.current_stage = "video_compile"
        state.status = "video_complete"

        LOGGER.info("Video Compiler Agent completed successfully.")

        return state