"""
AIStudio Subtitle Generator Agent

Generates subtitle/caption files (.srt) from narration audio
using the subtitle FastMCP server.

Author : AIStudio
"""

from __future__ import annotations

import logging
from pathlib import Path

from shared.models import ProjectState
from shared.services import PromptService

# Import tool directly from FastMCP server module
try:
    from servers.subtitle_server import generate_subtitles
except ImportError:
    generate_subtitles = None

LOGGER = logging.getLogger("SubtitleAgent")


class SubtitleAgent:
    """
    Generates word-level synchronized subtitle files (.srt) for the pipeline.
    """

    def __init__(self) -> None:
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream audio dependencies.
        """
        if state.audio is None and not hasattr(state, "master_audio_path") and not getattr(state, "master_audio", None):
            raise ValueError(
                "SubtitleAgent failure: Audio data or master audio must exist before SubtitleAgent runs."
            )

    def run(self, state: ProjectState) -> ProjectState:
        """
        Executes the subtitle generation step.
        """
        self._validate_state(state)

        LOGGER.info("Starting Subtitle Generator Agent")

        # Determine target audio file path from state
        audio_path = getattr(state, "master_audio_path", None)
        if not audio_path and state.master_audio:
            audio_path = getattr(state.master_audio, "filename", None)
        if not audio_path and state.audio:
            audio_path = getattr(state.audio, "master_audio_path", None) or getattr(state.audio, "filename", None)

        if not audio_path or not Path(str(audio_path)).exists():
            LOGGER.warning("No physical audio file found at path '%s' to generate subtitles. Skipping.", audio_path)
            state.current_stage = "subtitles"
            state.status = "subtitles_skipped"
            return state

        output_srt_path = Path(str(audio_path)).parent / "captions.srt"

        try:
            if generate_subtitles:
                srt_file = generate_subtitles(
                    audio_path=str(audio_path),
                    output_path=str(output_srt_path),
                )
                state.subtitle_file_path = str(srt_file)
                LOGGER.info("Subtitle file generated at %s", srt_file)
            else:
                LOGGER.error("Subtitle server function unavailable.")
                state.status = "failed"
                return state
        except Exception as err:
            raise RuntimeError(
                f"SubtitleAgent failure during caption generation: {err}"
            ) from err

        state.current_stage = "subtitles"
        state.status = "subtitles_complete"

        LOGGER.info("Subtitle Generator Agent completed successfully.")

        return state