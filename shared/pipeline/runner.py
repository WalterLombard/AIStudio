"""
AIStudio Pipeline Runner

Coordinates the complete AIStudio production pipeline.
Passes the ProjectState sequentially across specialized agent stages.

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
from agents.subtitle_generator import SubtitleAgent          # <--- Subtitle Engine Agent
from agents.video_compiler import VideoCompilerAgent
from agents.publisher import PublisherAgent                   # <--- Publisher/SEO Engine Agent


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
        self.shot_planner = ShotPlannerAgent()
        self.image_generator = ImageGeneratorAgent()
        self.motion_designer = MotionDesignerAgent()
        self.narration_designer = NarrationDesignerAgent()
        self.voice_generator = VoiceGeneratorAgent()
        self.music_generator = MusicGeneratorAgent()
        self.sfx_generator = SFXGeneratorAgent()
        self.audio_mixer = AudioMixerAgent()
        self.subtitle_generator = SubtitleAgent()             # <--- Subtitle initialization
        self.video_compiler = VideoCompilerAgent()
        self.publisher = PublisherAgent()                     # <--- Publisher initialization

    def _execute_stage(self, agent_name: str, agent_instance: object, state_or_input: object) -> ProjectState:
        """
        Executes a single pipeline agent stage with error handling and status updates.
        """
        LOGGER.info(f"--> [Stage Start]: Executing {agent_name}")
        
        try:
            state = agent_instance.run(state_or_input)
            state.current_stage = agent_name
            state.status = "in_progress"
            LOGGER.info(f"--> [Stage Complete]: {agent_name} succeeded.")
            return state

        except Exception as ex:
            LOGGER.error(f"❌ Failure during stage '{agent_name}': {ex}", exc_info=True)
            if isinstance(state_or_input, ProjectState):
                state_or_input.status = "failed"
                state_or_input.current_stage = agent_name
                return state_or_input
            raise ex

    def run(self, user_request: str) -> ProjectState:
        """
        Execute the complete production pipeline sequentially.
        """
        LOGGER.info("Starting AIStudio Production Pipeline")

        # 1. Executive Producer
        state = self._execute_stage("ExecutiveProducer", self.executive_producer, user_request)
        if state.status == "failed": return state

        # 2. Research
        state = self._execute_stage("ResearchAgent", self.research, state)
        if state.status == "failed": return state

        # 3. Outline
        state = self._execute_stage("OutlineAgent", self.outline, state)
        if state.status == "failed": return state

        # 4. Script
        state = self._execute_stage("ScriptWriterAgent", self.script, state)
        if state.status == "failed": return state

        # 5. Storyboard
        state = self._execute_stage("StoryboardAgent", self.storyboard, state)
        if state.status == "failed": return state

        # 6. Visual Planner
        state = self._execute_stage("VisualPlannerAgent", self.visual_planner, state)
        if state.status == "failed": return state

        # 7. Shot Planner
        state = self._execute_stage("ShotPlannerAgent", self.shot_planner, state)
        if state.status == "failed": return state

        # 8. Image Generator
        state = self._execute_stage("ImageGeneratorAgent", self.image_generator, state)
        if state.status == "failed": return state

        # 9. Motion Designer
        state = self._execute_stage("MotionDesignerAgent", self.motion_designer, state)
        if state.status == "failed": return state

        # 10. Narration Designer
        state = self._execute_stage("NarrationDesignerAgent", self.narration_designer, state)
        if state.status == "failed": return state

        # 11. Voice Generator
        state = self._execute_stage("VoiceGeneratorAgent", self.voice_generator, state)
        if state.status == "failed": return state

        # 12. Music Generator
        state = self._execute_stage("MusicGeneratorAgent", self.music_generator, state)
        if state.status == "failed": return state

        # 13. SFX Generator
        state = self._execute_stage("SFXGeneratorAgent", self.sfx_generator, state)
        if state.status == "failed": return state

        # 14. Audio Mixer
        state = self._execute_stage("AudioMixerAgent", self.audio_mixer, state)
        if state.status == "failed": return state

        # 15. Subtitle Generator (Calls subtitle_server.py)
        state = self._execute_stage("SubtitleAgent", self.subtitle_generator, state)
        if state.status == "failed": return state

        # 16. Video Compiler (Calls compiler_server.py)
        state = self._execute_stage("VideoCompilerAgent", self.video_compiler, state)
        if state.status == "failed": return state

        # 17. Publisher (Calls publisher_server.py for packaging & metadata)
        state = self._execute_stage("PublisherAgent", self.publisher, state)
        if state.status == "failed": return state

        state.status = "completed"
        LOGGER.info("AIStudio Production Pipeline Completed Successfully!")

        return state