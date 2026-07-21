"""
AIStudio Research Agent

Builds the complete ResearchData object using multiple focused LLM
requests rather than one enormous prompt.

Each research section is generated independently. This improves:

- reliability
- JSON accuracy
- retry capability
- future parallelisation

Author : AIStudio
"""

from __future__ import annotations

import json
import logging

from shared.models import (
    BackgroundResponse,
    FactsResponse,
    MisconceptionsResponse,
    ProductionResponse,
    ProjectState,
    ReferencesResponse,
    ResearchData,
)

from shared.services import (
    LLMService,
    PromptService,
)

LOGGER = logging.getLogger("ResearchAgent")


class ResearchAgent:
    """
    Generates the complete research package.

    The research package is intentionally generated in multiple
    independent LLM calls.

    Smaller prompts produce significantly higher quality output,
    reduce hallucinations and allow future retry of individual
    sections.
    """

    def __init__(self) -> None:

        self.llm = LLMService()

        self.system_prompt = PromptService.load_prompt(
            __file__,
        )

    def _generate_section(
        self,
        task: str,
        production_brief: dict,
    ) -> dict:
        """
        Generate one section of the research package.
        """

        LOGGER.info(
            "Generating research section: %s",
            task,
        )

        prompt = json.dumps(

            {
                "task": task,
                "production_brief": production_brief,
            },

            indent=4,

            ensure_ascii=False,

        )

        result = self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.20,

        )

        LOGGER.info(
            "Completed research section: %s",
            task,
        )

        return result

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Build the complete ResearchData object.
        """

        if state.production_brief is None:

            raise ValueError(
                "ProductionBrief must exist before ResearchAgent runs."
            )

        LOGGER.info(
            "Starting Research Agent"
        )

        production_brief = (
            state.production_brief.model_dump()
        )

        research = ResearchData()

        #
        # -------------------------------------------------------
        # BACKGROUND
        # -------------------------------------------------------
        #

        background = BackgroundResponse(

            **self._generate_section(

                task="background",

                production_brief=production_brief,

            )

        )

        research.executive_summary = background.executive_summary

        research.historical_background = background.historical_background

        research.scientific_background = background.scientific_background

        #
        # -------------------------------------------------------
        # FACTS
        # -------------------------------------------------------
        #

        facts = FactsResponse(

            **self._generate_section(

                task="facts",

                production_brief=production_brief,

            )

        )

        research.facts = facts.facts

        research.statistics = facts.statistics

        research.timeline = facts.timeline

        research.technical_terms = facts.technical_terms

        #
        # -------------------------------------------------------
        # MISCONCEPTIONS
        # -------------------------------------------------------
        #

        misconceptions = MisconceptionsResponse(

            **self._generate_section(

                task="misconceptions",

                production_brief=production_brief,

            )

        )

        research.misconceptions = misconceptions.misconceptions

        #
        # -------------------------------------------------------
        # PRODUCTION
        # -------------------------------------------------------
        #

        production = ProductionResponse(

            **self._generate_section(

                task="production",

                production_brief=production_brief,

            )

        )

        research.visual_opportunities = production.visual_opportunities

        research.broll_opportunities = production.broll_opportunities

        research.cinematic_moments = production.cinematic_moments

        research.emotional_beats = production.emotional_beats

        research.narration_highlights = production.narration_highlights

        #
        # -------------------------------------------------------
        # REFERENCES
        # -------------------------------------------------------
        #

        references = ReferencesResponse(

            **self._generate_section(

                task="references",

                production_brief=production_brief,

            )

        )

        research.important_people = references.important_people

        research.important_locations = references.important_locations

        research.search_keywords = references.search_keywords

        research.related_topics = references.related_topics

        research.verification_notes = references.verification_notes

        #
        # Save into pipeline state
        #

        state.research = research

        state.current_stage = "research"

        state.status = "research_complete"

        LOGGER.info(
            "Research Agent completed successfully."
        )

        return state