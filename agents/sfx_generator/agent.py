"""
AIStudio Sound Effects Generator

Generates documentary sound effects for every approved storyboard shot.

The Sound Effects Generator translates the approved motion and narration
plans into environmental sound effect cues. Each cue is subsequently
executed by the SFXService to generate production-ready sound assets.

Produced by the Sound Design department.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    AssetRecord,
    ProjectState,
    SFXAsset,
    SFXCue,
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
    Generates documentary sound effects for every approved storyboard shot.
    """

    def __init__(self) -> None:
        """
        Initialise required services.
        """

        self.llm = LLMService()

        self.sfx = SFXService()

        self.assets = AssetService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _validate_state(
        self,
        state: ProjectState,
    ) -> None:
        """
        Validate required upstream state.
        """

        if state.motion is None:
            raise ValueError(
                "MotionData must exist before SFXGeneratorAgent runs."
            )

        if state.narration is None:
            raise ValueError(
                "NarrationData must exist before SFXGeneratorAgent runs."
            )

    def _build_payload(
        self,
        motion: dict,
        narration: dict,
    ) -> str:
        """
        Build the LLM payload.
        """

        payload = {
            "motion": motion,
            "narration": narration,
        }

        return json.dumps(
            payload,
            indent=4,
            ensure_ascii=False,
        )

    def _generate_cue(
        self,
        motion: dict,
        narration: dict,
    ) -> SFXCue:
        """
        Generate one sound effect cue.
        """

        prompt = self._build_payload(
            motion,
            narration,
        )

        result = self.llm.generate_json(
            system=self.system_prompt,
            prompt=prompt,
            temperature=0.20,
        )

        response = SFXSceneResponse(
            **result,
        )

        return response.cue

    def _generate_assets(
        self,
        plan: SFXData,
    ) -> SFXLibrary:
        """
        Generate all sound effect assets.
        """

        library = SFXLibrary()

        for cue in plan.cues:

            generated = self.sfx.generate(
                cue,
            )

            asset_record = AssetRecord(
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

            registered = self.assets.register(
                asset_record,
            )

            library.assets.append(

                SFXAsset(

                    asset_id=registered.asset_id,

                    scene_id=cue.scene_id,

                    shot_number=cue.shot_number,

                    image_asset_id=cue.image_asset_id,

                    provider=generated.provider,

                    filename=registered.filename,

                    duration=registered.duration,

                    metadata=generated.metadata,

                )

            )

        return library

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Execute the Sound Effects Generator.
        """

        self._validate_state(
            state,
        )

        plan = SFXData()

        for motion, narration in zip(

            state.motion.scenes,

            state.narration.segments,

            strict=False,

        ):

            cue = self._generate_cue(

                motion=motion.model_dump(),

                narration=narration.model_dump(),

            )

            plan.cues.append(
                cue,
            )

        state.sfx = self._generate_assets(
            plan,
        )

        state.current_stage = "sfx_generation"

        state.status = "sfx_complete"

        return state