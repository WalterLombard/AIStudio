"""
AIStudio Music Generator Agent

Generates the documentary music plan one shot at a time.

Each approved shot receives its own music cue. This keeps prompts
small, avoids LLM timeouts and allows regeneration of individual
shots.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    AssetRecord,
    MusicAsset,
    MusicData,
    MusicLibrary,
    MusicSceneResponse,
    ProjectState,
)

from shared.services import (
    AssetService,
    LLMService,
    MusicService,
    PromptService,
)


class MusicGeneratorAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.music = MusicService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_cue(
        self,
        motion: dict,
        narration: dict,
    ) -> MusicSceneResponse:
        """
        Generate one music cue.
        """

        prompt = json.dumps(

            {

                "motion": motion,

                "narration": narration,

            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return MusicSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.motion is None:

            raise ValueError(
                "MotionData must exist before MusicGeneratorAgent runs."
            )

        if state.narration is None:

            raise ValueError(
                "NarrationData must exist before MusicGeneratorAgent runs."
            )

        music_plan = MusicData()

        #
        # Generate one cue per shot
        #

        for motion, narration in zip(

            state.motion.moves,

            state.narration.segments,

            strict=False,

        ):

            response = self._generate_cue(

                motion.model_dump(),

                narration.model_dump(),

            )

            music_plan.cues.append(
                response.cue
            )

        #
        # Generate music assets
        #

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