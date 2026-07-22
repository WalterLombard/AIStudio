"""
AIStudio LLM Service

Provides a single interface for communicating with the configured
Large Language Model.

Every AI agent in AIStudio uses this service.

Author: AIStudio
"""

from __future__ import annotations

from typing import Any

import requests

from shared.config import config
from shared.exceptions import LLMResponseError
from shared.logger import get_logger
from shared.parsers.json_parser import JSONParser


LOGGER = get_logger("LLMService")


class LLMService:
    """
    Service responsible for all communication with the configured
    Large Language Model.
    """

    def __init__(self) -> None:
        self.provider = config.models.llm.provider.lower()
        self.model = config.models.llm.model
        self.endpoint = config.models.llm.endpoint
        self.temperature = config.models.llm.temperature
        self.num_predict = config.models.llm.num_predict

    def generate(
        self,
        system: str,
        prompt: str,
        temperature: float | None = None,
    ) -> str:
        """
        Generate plain text from the configured LLM.
        """
        if self.provider != "ollama":
            raise LLMResponseError(
                f"Unsupported LLM provider '{self.provider}'."
            )

        if temperature is None:
            temperature = self.temperature

        payload = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": self.num_predict,
            },
        }

        LOGGER.info("=" * 70)
        LOGGER.info("LLM REQUEST")
        LOGGER.info("=" * 70)
        LOGGER.info("Provider      : %s", self.provider)
        LOGGER.info("Model         : %s", self.model)
        LOGGER.info("Endpoint      : %s", self.endpoint)
        LOGGER.info("Temperature   : %.2f", temperature)
        LOGGER.info("Prompt Length : %d characters", len(prompt))

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()

        except requests.RequestException as ex:
            LOGGER.exception("Unable to communicate with the LLM.")
            raise LLMResponseError(
                f"Unable to communicate with the LLM: {ex}"
            ) from ex

        LOGGER.info("=" * 70)
        LOGGER.info("LLM RESPONSE")
        LOGGER.info("=" * 70)
        LOGGER.info("Model         : %s", data.get("model", "Unknown"))
        LOGGER.info("Done          : %s", data.get("done"))
        LOGGER.info("Done Reason   : %s", data.get("done_reason"))
        LOGGER.info("Prompt Tokens : %s", data.get("prompt_eval_count", 0))
        LOGGER.info("Output Tokens : %s", data.get("eval_count", 0))

        if "response" not in data:
            raise LLMResponseError("LLM returned an invalid response.")

        return data["response"].strip()

    def generate_json(
        self,
        system: str,
        prompt: str,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        """
        Generate JSON from the configured LLM.
        """
        text = self.generate(
            system=system,
            prompt=prompt,
            temperature=temperature,
        )

        LOGGER.info("=" * 70)
        LOGGER.info("JSON TO PARSE")
        LOGGER.info("=" * 70)
        LOGGER.info(text)
        LOGGER.info("=" * 70)

        try:
            parsed = JSONParser.parse(text)
            if isinstance(parsed, dict):
                return parsed
            return {"data": parsed}

        except Exception as ex:
            LOGGER.exception("LLM returned invalid JSON.")
            raise LLMResponseError(
                f"LLM did not return valid JSON: {ex}"
            ) from ex