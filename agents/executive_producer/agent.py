"""
AIStudio Executive Producer Agent

Creates the initial Production Brief from the user's request using LLM
or FastMCP executive producer server specifications.
This is the first AI agent in the AIStudio production pipeline.

Author : AIStudio
"""

from __future__ import annotations

import json
import logging
from typing import Any

from shared.models import (
    ProductionBrief,
    ProjectState,
)
from shared.services import (
    LLMService,
    PromptService,
)

# Optional import of FastMCP executive server module
try:
    from servers.executive_server import generate_production_brief
except ImportError:
    generate_production_brief = None

LOGGER = logging.getLogger("ExecutiveProducer")


class ExecutiveProducer:
    """
    Generates the initial Production Brief.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.system_prompt = PromptService.load_prompt(__file__)

    def _validate_inputs(self, user_request: str) -> None:
        """Validates that a non-empty user request was provided."""
        if not user_request or not user_request.strip():
            raise ValueError("ExecutiveProducer requires a valid, non-empty user_request.")

    def _build_payload(self, user_request: str) -> str:
        """Formats and serializes input payload for logging and deterministic passing."""
        payload = {"user_request": user_request}
        return json.dumps(payload, indent=4, ensure_ascii=False)

    def _generate_brief(self, user_request: str) -> ProductionBrief:
        """Calls the LLM service or FastMCP server and parses the result into ProductionBrief."""
        LOGGER.info("Generating production brief from user request...")

        try:
            if generate_production_brief:
                result = generate_production_brief(user_request=user_request)
            else:
                result = self.llm.generate_json(
                    system=self.system_prompt,
                    prompt=user_request,
                    temperature=0.4,
                )
        except Exception as err:
            raise RuntimeError(
                f"ExecutiveProducer failure during generation: {err}"
            ) from err

        try:
            if isinstance(result, ProductionBrief):
                return result

            if isinstance(result, dict):
                if "production_brief" in result and isinstance(result["production_brief"], dict):
                    return ProductionBrief(**result["production_brief"])
                elif "brief" in result and isinstance(result["brief"], dict):
                    return ProductionBrief(**result["brief"])
                else:
                    return ProductionBrief(**result)
            else:
                raise ValueError("Expected dictionary output from generation source.")
        except Exception as err:
            raise ValueError(
                f"ExecutiveProducer failed to validate output against ProductionBrief model: {err}"
            ) from err

    def run(
        self,
        user_request: str,
        state: ProjectState | None = None,
    ) -> ProjectState:
        """
        Executes the Executive Producer pipeline step.
        """
        self._validate_inputs(user_request)

        if state is None:
            state = ProjectState()

        brief = self._generate_brief(user_request)

        # Store the production brief
        state.production_brief = brief

        # Populate project metadata
        state.project_info.project_name = brief.title
        state.project_info.topic = brief.topic

        # Update pipeline state
        state.current_stage = "production_brief"
        state.status = "production_brief_complete"

        LOGGER.info("Executive Producer Agent completed successfully.")

        return state