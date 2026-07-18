"""
AIStudio Research Agent

Builds the complete ResearchData object using multiple focused LLM
requests rather than one very large request.

Author : AIStudio
"""

from __future__ import annotations

import json

from shared.models import (
    ProjectState,
    ResearchData,
)

from shared.services import (
    LLMService,
    PromptService,
)


class ResearchAgent:
    """
    Produces the complete ResearchData object.

    Multiple small prompts are considerably more reliable than
    one enormous prompt.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__
        )

    def _generate_section(
        self,
        task: str,
        production_brief: dict,
    ) -> dict:
        """
        Generate one section of the research.
        """

        prompt = json.dumps(

            {
                "task": task,
                "production_brief": production_brief,
            },

            indent=4,

            ensure_ascii=False,

        )

        return self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.2,

        )

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Build the research package.
        """

        if state.production_brief is None:

            raise ValueError(
                "ProjectState does not contain a ProductionBrief."
            )

        production_brief = state.production_brief.model_dump()

        research = ResearchData()

        # ======================================================
        # Background
        # ======================================================

        result = self._generate_section(

            "background",

            production_brief,

        )

        research.executive_summary = result.get(
            "executive_summary",
            "",
        )

        research.historical_background = result.get(
            "historical_background",
            "",
        )

        research.scientific_background = result.get(
            "scientific_background",
            "",
        )

        # ======================================================
        # Facts
        # ======================================================

        result = self._generate_section(

            "facts",

            production_brief,

        )

        research.facts = result.get(
            "facts",
            [],
        )

        research.statistics = result.get(
            "statistics",
            [],
        )

        research.timeline = result.get(
            "timeline",
            [],
        )

        research.technical_terms = result.get(
            "technical_terms",
            [],
        )

        # ======================================================
        # Misconceptions
        # ======================================================

        result = self._generate_section(

            "misconceptions",

            production_brief,

        )

        research.misconceptions = result.get(
            "misconceptions",
            [],
        )

        # ======================================================
        # Production Assets
        # ======================================================

        result = self._generate_section(

            "production",

            production_brief,

        )

        research.visual_opportunities = result.get(
            "visual_opportunities",
            [],
        )

        research.broll_opportunities = result.get(
            "broll_opportunities",
            [],
        )

        research.cinematic_moments = result.get(
            "cinematic_moments",
            [],
        )

        research.emotional_beats = result.get(
            "emotional_beats",
            [],
        )

        research.narration_highlights = result.get(
            "narration_highlights",
            [],
        )

        # ======================================================
        # References
        # ======================================================

        result = self._generate_section(

            "references",

            production_brief,

        )

        research.important_people = result.get(
            "important_people",
            [],
        )

        research.important_locations = result.get(
            "important_locations",
            [],
        )

        research.search_keywords = result.get(
            "search_keywords",
            [],
        )

        research.related_topics = result.get(
            "related_topics",
            [],
        )

        research.verification_notes = result.get(
            "verification_notes",
            [],
        )

        state.research = research

        return state