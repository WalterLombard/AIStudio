"""
AIStudio Music Generator Agent

Generates the documentary music plan one scene at a time.

Each scene is planned independently to keep prompts small,
avoid LLM timeouts and allow failed scenes to be regenerated
without rerunning the entire music plan.

After planning completes, the MusicService generates the
actual music assets.

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

    def _generate_scene(
        self,
        motion_scene: dict,
        narration_scene: dict,
    ) -> MusicSceneResponse:
        """
        Generate one music cue.
        """

        prompt = json.dumps(

            {
                "motion_scene": motion_scene,
                "narration_scene": narration_scene,
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
                "ProjectState does not contain MotionData."
            )

        if state.narration is None:

            raise ValueError(
                "ProjectState does not contain NarrationData."
            )

        music_plan = MusicData()

        #
        # Generate one cue per scene
        #

        for motion_scene, narration_scene in zip(

            state.motion.scenes,

            state.narration.scenes,

        ):

            response = self._generate_scene(

                motion_scene=motion_scene.model_dump(),

                narration_scene=narration_scene.model_dump(),

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