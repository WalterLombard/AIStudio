"""
AIStudio Scene State

Stores every piece of information for one documentary scene.

Author : AIStudio
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .outline import OutlineScene
from .script import ScriptScene
from .storyboard import StoryboardScene
from .visuals import VisualAsset
from .shot import ShotSpecification
from .images import ImageAsset
from .motion import CameraMove
from .narration import NarrationSegment
from .music import MusicCue, MusicAsset
from .sfx import SFXCue, SFXAsset
from .audio import AudioAsset


class SceneState(BaseModel):
    """
    Complete production state for one documentary scene.
    """

    scene_number: int

    outline: OutlineScene | None = None

    script: ScriptScene | None = None

    storyboard: StoryboardScene | None = None

    visuals: list[VisualAsset] = Field(
        default_factory=list
    )

    shots: list[ShotSpecification] = Field(
        default_factory=list
    )

    images: list[ImageAsset] = Field(
        default_factory=list
    )

    motion: CameraMove | None = None

    narration: NarrationSegment | None = None

    music_plan: MusicCue | None = None

    music_asset: MusicAsset | None = None

    sfx_plan: list[SFXCue] = Field(
        default_factory=list
    )

    sfx_assets: list[SFXAsset] = Field(
        default_factory=list
    )

    narration_audio: AudioAsset | None = None