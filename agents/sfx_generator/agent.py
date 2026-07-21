"""
AIStudio Sound Effects Generator

Generates documentary sound effects one scene at a time.

Each scene is planned independently to keep prompts small,
avoid LLM timeouts and allow failed scenes to be regenerated
without rerunning the entire sound effects plan.

After planning completes, the SFXService generates the
actual sound effect assets.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    AssetRecord,
    ProjectState,
    SFXAsset,
    SFXData,
    SFXLibrary,
    SFXSceneResponse,
)

from shared.services import (
    AssetService,
    LLMService,
    PromptService,
    SFXService,
)


class SFXGeneratorAgent:

    def __init__(self) -> None:

        self.llm = LLMService()

        self.sfx = SFXService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_scene(
        self,
        storyboard_scene: dict,
        motion_scene: dict,
    ) -> SFXSceneResponse:
        """
        Generate one sound effects cue.
        """

        prompt = json.dumps(

            {
                "storyboard_scene": storyboard_scene,
                "motion_scene": motion_scene,
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        return SFXSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.motion is None:

            raise ValueError(
                "ProjectState does not contain MotionData."
            )

        if state.storyboard is None:

            raise ValueError(
                "ProjectState does not contain StoryboardData."
            )

        plan = SFXData()

        #
        # Generate one cue per scene
        #

        for storyboard_scene, motion_scene in zip(

            state.storyboard.scenes,

            state.motion.scenes,

        ):

            response = self._generate_scene(

                storyboard_scene=storyboard_scene.model_dump(),

                motion_scene=motion_scene.model_dump(),

            )

            plan.cues.append(
                response.cue
            )

        #
        # Generate SFX assets
        #

        library = SFXLibrary()

        for cue in plan.cues:

            generated = self.sfx.generate(
                cue
            )

            asset = AssetRecord(

                asset_type="sfx",

                stage="sfx_generation",

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

                SFXAsset(

                    asset_id=asset.asset_id,

                    scene_id=cue.scene_id,

                    filename=asset.filename,

                    duration=asset.duration,

                )

            )

        state.sfx = library

        state.current_stage = "sfx_generation"

        state.status = "sfx_complete"

        return state