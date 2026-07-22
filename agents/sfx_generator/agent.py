"""
AIStudio Sound Effects Generator

Generates documentary sound effects one shot at a time.

Each approved shot receives its own sound effects plan. This keeps
prompts small, avoids LLM timeouts and allows regeneration of
individual shots.

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
    """
    Generates documentary sound effects one shot at a time.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.sfx = SFXService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_cue(
        self,
        motion: dict,
        narration: dict,
    ) -> SFXSceneResponse:
        """
        Generate sound effects for one shot.
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

        return SFXSceneResponse(**result)

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:

        if state.motion is None:

            raise ValueError(
                "MotionData must exist before SFXGeneratorAgent runs."
            )

        if state.narration is None:

            raise ValueError(
                "NarrationData must exist before SFXGeneratorAgent runs."
            )

        plan = SFXData()

        #
        # Generate one cue per shot
        #

        for motion, narration in zip(

            state.motion.scenes,

            state.narration.segments,

            strict=False,

        ):

            response = self._generate_cue(

                motion=motion.model_dump(),

                narration=narration.model_dump(),

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

                metadata={
                    **generated.metadata,
                    "shot_number": cue.shot_number,
                    "image_asset_id": cue.image_asset_id,
                },

            )

            asset = self.assets.register(
                asset
            )

            library.assets.append(

                SFXAsset(

                    asset_id=asset.asset_id,

                    scene_id=cue.scene_id,

                    shot_number=cue.shot_number,

                    image_asset_id=cue.image_asset_id,

                    filename=asset.filename,

                    duration=asset.duration,

                )

            )

        state.sfx = library

        state.current_stage = "sfx_generation"

        state.status = "sfx_complete"

        return state