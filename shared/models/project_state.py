"""
AIStudio Project State

Central state object shared by every AI agent.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel

from .project import ProjectInfo
from .production_brief import ProductionBrief
from .research import ResearchData
from .outline import OutlineData
from .script import ScriptData
from .storyboard import StoryboardData
from .visuals import VisualData
from .images import ImageData
from .motion import MotionData
from .narration import NarrationData
from .audio import AudioData
from .music import MusicLibrary
from .sfx import SFXLibrary
from .master_audio import MasterAudioData
from .video import VideoData
from .qa import QAReport


class ProjectState(BaseModel):

    project: ProjectInfo = ProjectInfo()

    production_brief: ProductionBrief | None = None

    research: ResearchData | None = None

    outline: OutlineData | None = None

    script: ScriptData | None = None

    storyboard: StoryboardData | None = None

    visuals: VisualData | None = None

    images: ImageData | None = None

    motion: MotionData | None = None

    narration: NarrationData | None = None

    audio: AudioData | None = None

    music: MusicLibrary | None = None

    sfx: SFXLibrary | None = None

    master_audio: MasterAudioData | None = None

    video: VideoData | None = None

    qa: QAReport | None = None

    current_stage: str = "created"

    status: str = "idle"