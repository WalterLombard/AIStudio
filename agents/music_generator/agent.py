"""
AIStudio Music Generator Agent

Creates the complete background music plan and generates the
music assets.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    AssetRecord,
    MusicAsset,
    MusicData,
    MusicLibrary,
    ProjectState,
)

from shared.services import (
    AssetService,
    LLMService,
    MusicService,
    PromptService,
)


class MusicGeneratorAgent:
    """
    Produces documentary background music.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.music = MusicService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.motion is None:

            raise ValueError(
                "ProjectState does not contain MotionData."
            )

        if state.narration is None:

            raise ValueError(
                "ProjectState does not contain NarrationData."
            )

        prompt = json.dumps(

            {

                "motion":
                    state.motion.model_dump(),

                "narration":
                    state.narration.model_dump(),

            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        music_plan = MusicData(
            **result
        )

        library = MusicLibrary()

        for cue in music_plan.cues:

            generated = self.music.generate(
                cue
            )

            asset = AssetRecord(

                asset_type="music",

                stage="music_generation",

                provider=generated.provider,

                filename=generated.filename,

                source_scene=cue.scene_id,

                duration=generated.duration,

                metadata=generated.metadata,

            )

            asset = self.assets.register(
                asset
            )

            library.assets.append(

                MusicAsset(

                    asset_id=asset.asset_id,

                    scene_id=cue.scene_id,

                    filename=asset.filename,

                    duration=asset.duration,

                )

            )

        state.music = library

        state.current_stage = "music_generation"

        state.status = "music_complete"

        return state