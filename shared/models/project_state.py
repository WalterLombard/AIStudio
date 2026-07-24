"""
AIStudio Project State

Central state object shared by every AI agent.

Every stage of the AIStudio production pipeline receives the same
ProjectState instance, enriches it with additional data and returns
the updated state to the Pipeline Runner.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .audio import AudioData
from .images import ImageData
from .master_audio import MasterAudioData
from .motion import MotionData
from .music import MusicLibrary
from .narration import NarrationData
from .outline import OutlineData
from .production_brief import ProductionBrief
from .project import ProjectInfo
from .qa import QAReport
from .research import ResearchData
from .script import ScriptData
from .sfx import SFXLibrary
from .shot import ShotData
from .storyboard import StoryboardData
from .video import VideoData
from .visuals import VisualData


class ProjectState(BaseModel):
    """
    Global state shared by every AIStudio agent.
    """

    #
    # Project information
    #

    project: ProjectInfo = Field(
        default_factory=ProjectInfo,
    )

    #
    # Executive Producer
    #

    production_brief: ProductionBrief | None = None

    #
    # Research
    #

    research: ResearchData | None = None

    #
    # Outline
    #

    outline: OutlineData | None = None

    #
    # Script
    #

    script: ScriptData | None = None

    #
    # Storyboard
    #

    storyboard: StoryboardData | None = None

    #
    # Visual Planning
    #

    visuals: VisualData | None = None

    shots: ShotData | None = None

    images: ImageData | None = None

    motion: MotionData | None = None

    #
    # Audio
    #

    narration: NarrationData | None = None

    audio: AudioData | None = None

    music: MusicLibrary | None = None

    sfx: SFXLibrary | None = None

    master_audio: MasterAudioData | None = None

    #
    # Final Video
    #

    video: VideoData | None = None

    #
    # Quality Assurance
    #

    qa: QAReport | None = None

    #
    # Pipeline Status
    #

    current_stage: str = "created"

    status: str = "idle"