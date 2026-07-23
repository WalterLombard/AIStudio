"""
AIStudio Research Agent

Builds the complete ResearchData object using multiple focused LLM
requests or FastMCP research server specifications.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging
from typing import Type, TypeVar

from pydantic import BaseModel

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

# Optional import of FastMCP research server module
try:
    from servers.research_server import generate_research_section
except ImportError:
    generate_research_section = None

LOGGER = logging.getLogger("ResearchAgent")

T = TypeVar("T", bound=BaseModel)


class ResearchAgent:
    """
    Generates the complete research package across multiple focused sub-tasks using compact state memory.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_state(self, state: ProjectState) -> None:
        """
        Validates required upstream dependencies before processing.
        """
        if state.production_brief is None:
            raise ValueError(
                "ResearchAgent failure: ProductionBrief must exist in ProjectState before ResearchAgent runs."
            )

    def _generate_and_validate_section(
        self,
        task: str,
        production_brief: dict,
        outline_summary: list[dict],
        response_model: Type[T],
    ) -> T:
        """
        Generates a research section and validates the response against the target Pydantic model.
        """
        LOGGER.info("Generating research section: %s", task)

        try:
            if generate_research_section and hasattr(generate_research_section, "generate_section_with_context"):
                result = generate_research_section(
                    task=task,
                    production_brief=production_brief,
                    outline_summary=outline_summary,
                )
            elif generate_research_section:
                result = generate_research_section(
                    task=task,
                    production_brief=production_brief,
                )
            else:
                prompt_payload = {
                    "task": task,
                    "production_brief": production_brief,
                    "outline_summary": outline_summary,
                }
                prompt = json.dumps(
                    prompt_payload,
                    indent=4,
                    ensure_ascii=False,
                )
                result = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=prompt,
                    temperature=0.20,
                )
        except Exception as err:
            raise RuntimeError(
                f"ResearchAgent failure during generation for task '{task}': {err}"
            ) from err

        try:
            if isinstance(result, response_model):
                validated_response = result
            else:
                validated_response = response_model(**result)

            LOGGER.info("Successfully validated research section: %s", task)
            return validated_response
        except Exception as err:
            raise ValueError(
                f"ResearchAgent failed to validate task '{task}' output against {response_model.__name__}: {err}"
            ) from err

    def run(
        self,
        state: ProjectState,
    ) -> ProjectState:
        """
        Builds and validates the complete ResearchData object using memory integration.
        """
        self._validate_state(state)

        LOGGER.info("Starting Research Agent")

        production_brief = state.production_brief.model_dump() if state.production_brief else {}

        # Retrieve outline overview from memory if available
        outline_summary = (
            state.memory.get_compact_outline_summary()
            if state.memory and hasattr(state.memory, "get_compact_outline_summary")
            else []
        )

        research_kwargs = {}

        # 1. Background
        background = self._generate_and_validate_section(
            task="background",
            production_brief=production_brief,
            outline_summary=outline_summary,
            response_model=BackgroundResponse,
        )
        research_kwargs.update(background.model_dump())

        # 2. Facts
        facts = self._generate_and_validate_section(
            task="facts",
            production_brief=production_brief,
            outline_summary=outline_summary,
            response_model=FactsResponse,
        )
        research_kwargs.update(facts.model_dump())

        # 3. Misconceptions
        misconceptions = self._generate_and_validate_section(
            task="misconceptions",
            production_brief=production_brief,
            outline_summary=outline_summary,
            response_model=MisconceptionsResponse,
        )
        research_kwargs.update(misconceptions.model_dump())

        # 4. Production
        production = self._generate_and_validate_section(
            task="production",
            production_brief=production_brief,
            outline_summary=outline_summary,
            response_model=ProductionResponse,
        )
        research_kwargs.update(production.model_dump())

        # 5. References
        references = self._generate_and_validate_section(
            task="references",
            production_brief=production_brief,
            outline_summary=outline_summary,
            response_model=ReferencesResponse,
        )
        research_kwargs.update(references.model_dump())

        # Instantiate consolidated ResearchData
        state.research = ResearchData(**research_kwargs)

        # Update pipeline state
        state.current_stage = "research"
        state.status = "research_complete"

        LOGGER.info("Research Agent completed successfully.")

        return state