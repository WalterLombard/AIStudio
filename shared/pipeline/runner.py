"""
AIStudio Pipeline Runner

Coordinates the complete AIStudio production pipeline.

The Pipeline Runner contains NO AI logic.

Its responsibility is simply to execute each agent in the correct
sequence while passing the ProjectState between them.

Author : AIStudio
"""

from __future__ import annotations

import logging

from shared.models import ProjectState

from agents.executive_producer import ExecutiveProducer
from agents.researcher import ResearchAgent
from agents.outline import OutlineAgent
from agents.script_writer import ScriptWriterAgent
from agents.storyboard import StoryboardAgent
from agents.visual_planner import VisualPlannerAgent
from agents.shot_planner import ShotPlannerAgent
from agents.image_generator import ImageGeneratorAgent
from agents.motion_designer import MotionDesignerAgent
from agents.narration_designer import NarrationDesignerAgent
from agents.voice_generator import VoiceGeneratorAgent
from agents.music_generator import MusicGeneratorAgent
from agents.sfx_generator import SFXGeneratorAgent
from agents.audio_mixer import AudioMixerAgent
from agents.video_compiler import VideoCompilerAgent


LOGGER = logging.getLogger("PipelineRunner")


class PipelineRunner:
    """
    Executes the complete AIStudio production pipeline.
    """

    def __init__(self) -> None:

        self.executive_producer = ExecutiveProducer()

        self.research = ResearchAgent()

        self.outline = OutlineAgent()

        self.script = ScriptWriterAgent()

        self.storyboard = StoryboardAgent()

        self.visual_planner = VisualPlannerAgent()

        #
        # NEW
        #
        self.shot_planner = ShotPlannerAgent()

        self.image_generator = ImageGeneratorAgent()

        self.motion_designer = MotionDesignerAgent()

        self.narration_designer = NarrationDesignerAgent()

        self.voice_generator = VoiceGeneratorAgent()

        self.music_generator = MusicGeneratorAgent()

        self.sfx_generator = SFXGeneratorAgent()

        self.audio_mixer = AudioMixerAgent()

        self.video_compiler = VideoCompilerAgent()

    def run(
        self,
        user_request: str,
    ) -> ProjectState:
        """
        Execute the complete production pipeline.
        """

        LOGGER.info(
            "Starting AIStudio Production Pipeline"
        )

        state = self.executive_producer.run(
            user_request
        )

        state = self.research.run(
            state
        )

        state = self.outline.run(
            state
        )

        state = self.script.run(
            state
        )

        state = self.storyboard.run(
            state
        )

        state = self.visual_planner.run(
            state
        )

        #
        # NEW STAGE
        #
        state = self.shot_planner.run(
            state
        )

        state = self.image_generator.run(
            state
        )

        state = self.motion_designer.run(
            state
        )

        state = self.narration_designer.run(
            state
        )

        state = self.voice_generator.run(
            state
        )

        state = self.music_generator.run(
            state
        )

        state = self.sfx_generator.run(
            state
        )

        state = self.audio_mixer.run(
            state
        )

        state = self.video_compiler.run(
            state
        )

        LOGGER.info(
            "AIStudio Production Pipeline Complete"
        )

        return state