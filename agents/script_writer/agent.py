"""
AIStudio Script Writer Agent

Generates the complete documentary narration from the approved
Production Brief, Research package and Outline.

The Script Writer is responsible for transforming the documentary
structure into natural narration suitable for voice synthesis while
maintaining pacing, viewer engagement and cinematic storytelling.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    ProjectState,
    ScriptData,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("ScriptWriterAgent")


class ScriptWriterAgent:
    """
    Produces the complete documentary narration.

    Input
    -----
    ProductionBrief
    ResearchData
    OutlineData

    Output
    ------
    ScriptData
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Generate the documentary narration.

        Parameters
        ----------
        state
            Current project state.

        Returns
        -------
        Updated ProjectState
        """

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief must exist before ScriptWriterAgent runs."
            )

        if state.research is None:

            raise ValueError(
                "ResearchData must exist before ScriptWriterAgent runs."
            )

        if state.outline is None:

            raise ValueError(
                "OutlineData must exist before ScriptWriterAgent runs."
            )

        LOGGER.info(
            "Starting Script Writer Agent"
        )

        prompt = json.dumps(

            {
                "production_brief":
                    state.production_brief.model_dump(),

                "research":
                    state.research.model_dump(),

                "outline":
                    state.outline.model_dump(),
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.25,

        )

        script = ScriptData(**result)

        state.script = script

        state.current_stage = "script"

        state.status = "script_complete"

        LOGGER.info(
            "Script Writer Agent completed successfully."
        )

        return state