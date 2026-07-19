"""
AIStudio Sound Effects Generator

Generates cinematic sound effects for every documentary scene.

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
)

from shared.services import (
    AssetService,
    LLMService,
    PromptService,
    SFXService,
)


class SFXGeneratorAgent:
    """
    Produces documentary sound effects.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.sfx = SFXService()

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

        if state.storyboard is None:

            raise ValueError(
                "ProjectState does not contain StoryboardData."
            )

        prompt = json.dumps(

            {

                "storyboard":
                    state.storyboard.model_dump(),

                "motion":
                    state.motion.model_dump(),

            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        plan = SFXData(
            **result
        )

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