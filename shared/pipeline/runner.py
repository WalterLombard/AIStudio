"""
AIStudio Pipeline Runner

Coordinates the complete AIStudio production pipeline.

The Pipeline Runner contains no AI logic. Its responsibility is to
execute each production agent in sequence, maintain the shared
ProjectState, log execution progress and provide a single entry point
into AIStudio.

Author : AIStudio
"""

from __future__ import annotations

from time import perf_counter
from typing import Protocol

from agents.audio_mixer import AudioMixerAgent
from agents.executive_producer import ExecutiveProducer
from agents.image_generator import ImageGeneratorAgent
from agents.motion_designer import MotionDesignerAgent
from agents.music_generator import MusicGeneratorAgent
from agents.narration_designer import NarrationDesignerAgent
from agents.outline import OutlineAgent
from agents.researcher import ResearchAgent
from agents.script_writer import ScriptWriterAgent
from agents.sfx_generator import SFXGeneratorAgent
from agents.shot_planner import ShotPlannerAgent
from agents.storyboard import StoryboardAgent
from agents.video_compiler import VideoCompilerAgent
from agents.visual_planner import VisualPlannerAgent
from agents.voice_generator import VoiceGeneratorAgent

from shared.logger import get_logger
from shared.models import ProjectState


class PipelineAgent(Protocol):
    """
    Standard interface implemented by every AIStudio production agent.
    """

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        ...


LOGGER = get_logger("PipelineRunner")


class PipelineRunner:
    """
    Executes the complete AIStudio production pipeline.
    """

    def __init__(self) -> None:
        """
        Initialise every production agent.
        """

        self.executive_producer = ExecutiveProducer()

        self.research = ResearchAgent()

        self.outline = OutlineAgent()

        self.script = ScriptWriterAgent()

        self.storyboard = StoryboardAgent()

        self.visual_planner = VisualPlannerAgent()

        self.shot_planner = ShotPlannerAgent()

        self.image_generator = ImageGeneratorAgent()

        self.motion_designer = MotionDesignerAgent()

        self.narration_designer = NarrationDesignerAgent()

        self.voice_generator = VoiceGeneratorAgent()

        self.music_generator = MusicGeneratorAgent()

        self.sfx_generator = SFXGeneratorAgent()

        self.audio_mixer = AudioMixerAgent()

        self.video_compiler = VideoCompilerAgent()

    def _run_stage(
        self,
        stage_name: str,
        agent: PipelineAgent,
        state: ProjectState,
    ) -> ProjectState:
        """
        Execute a single production stage.
        """

        LOGGER.info("=" * 70)

        LOGGER.info(
            "Starting Stage : %s",
            stage_name,
        )

        start = perf_counter()

        state = agent.run(
            state,
        )

        elapsed = perf_counter() - start

        LOGGER.info(
            "Completed Stage : %s (%.2f seconds)",
            stage_name,
            elapsed,
        )

        return state

    def run(
        self,
        user_request: str,
    ) -> ProjectState:
        """
        Execute the complete AIStudio production pipeline.
        """

        LOGGER.info("=" * 70)

        LOGGER.info(
            "AIStudio Production Pipeline Started",
        )

        pipeline_start = perf_counter()

        state = self.executive_producer.run(
            user_request,
        )

        state = self._run_stage(
            "Research",
            self.research,
            state,
        )

        state = self._run_stage(
            "Outline",
            self.outline,
            state,
        )

        state = self._run_stage(
            "Script Writer",
            self.script,
            state,
        )

        state = self._run_stage(
            "Storyboard",
            self.storyboard,
            state,
        )

        state = self._run_stage(
            "Visual Planner",
            self.visual_planner,
            state,
        )

        state = self._run_stage(
            "Shot Planner",
            self.shot_planner,
            state,
        )

        state = self._run_stage(
            "Image Generator",
            self.image_generator,
            state,
        )

        state = self._run_stage(
            "Motion Designer",
            self.motion_designer,
            state,
        )

        state = self._run_stage(
            "Narration Designer",
            self.narration_designer,
            state,
        )

        state = self._run_stage(
            "Voice Generator",
            self.voice_generator,
            state,
        )

        state = self._run_stage(
            "Music Generator",
            self.music_generator,
            state,
        )

        state = self._run_stage(
            "SFX Generator",
            self.sfx_generator,
            state,
        )

        state = self._run_stage(
            "Audio Mixer",
            self.audio_mixer,
            state,
        )

        state = self._run_stage(
            "Video Compiler",
            self.video_compiler,
            state,
        )

        total = perf_counter() - pipeline_start

        LOGGER.info("=" * 70)

        LOGGER.info(
            "AIStudio Production Pipeline Complete",
        )

        LOGGER.info(
            "Total Runtime : %.2f seconds",
            total,
        )

        LOGGER.info("=" * 70)

        return state