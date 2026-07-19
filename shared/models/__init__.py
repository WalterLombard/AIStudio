"""
AIStudio Shared Models
"""

from .project import ProjectInfo
from .production_brief import ProductionBrief

from .research import ResearchData, ResearchSource
from .outline import OutlineData
from .script import ScriptData
from .storyboard import StoryboardData

from .visuals import VisualAsset, VisualData
from .images import ImageAsset, ImageData

from .motion import CameraMove, MotionData

from .narration import NarrationSegment, NarrationData

from .audio import AudioAsset, AudioData

from .music import MusicCue, MusicData, MusicAsset, MusicLibrary

from .sfx import SFXCue, SFXData, SFXAsset, SFXLibrary

from .master_audio import MasterAudioData

from .video import VideoData

from .qa import QAReport

from .asset import AssetRecord, AssetRegistry

from .project_state import ProjectState