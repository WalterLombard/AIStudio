"""
AIStudio LLM Service

Provides a single interface for communicating with the configured
Large Language Model.

Every AI agent in AIStudio uses this service.

Author: AIStudio
"""

from __future__ import annotations

import json
from typing import Any

import requests

from shared.config import config
from shared.exceptions import LLMResponseError
from shared.logger import get_logger


LOGGER = get_logger("LLMService")

REQUEST_TIMEOUT = 300

SUPPORTED_PROVIDERS = {
    "ollama",
}


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

    def _build_payload(
        self,
        system: str,
        prompt: str,
        temperature: float,
    ) -> dict[str, Any]:
        """
        Build the provider request payload.
        """

        return {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": self.num_predict,
            },
        }

    def _log_request(
        self,
        temperature: float,
        prompt: str,
    ) -> None:
        """
        Log the outbound request.
        """

        LOGGER.info("=" * 70)
        LOGGER.info("LLM REQUEST")
        LOGGER.info("=" * 70)
        LOGGER.info("Provider      : %s", self.provider)
        LOGGER.info("Model         : %s", self.model)
        LOGGER.info("Endpoint      : %s", self.endpoint)
        LOGGER.info("Temperature   : %.2f", temperature)
        LOGGER.info("Prompt Length : %d characters", len(prompt))

    def _send_request(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send the request to the configured LLM.
        """

        try:

            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as ex:

            LOGGER.exception(
                "Unable to communicate with the LLM."
            )

            raise LLMResponseError(
                f"Unable to communicate with the LLM: {ex}"
            ) from ex

    def _log_response(
        self,
        data: dict[str, Any],
    ) -> None:
        """
        Log the inbound response.
        """

        LOGGER.info("=" * 70)
        LOGGER.info("LLM RESPONSE")
        LOGGER.info("=" * 70)
        LOGGER.info(
            "Model         : %s",
            data.get("model", "Unknown"),
        )
        LOGGER.info(
            "Done          : %s",
            data.get("done"),
        )
        LOGGER.info(
            "Done Reason   : %s",
            data.get("done_reason"),
        )
        LOGGER.info(
            "Prompt Tokens : %s",
            data.get("prompt_eval_count", 0),
        )
        LOGGER.info(
            "Output Tokens : %s",
            data.get("eval_count", 0),
        )

    @staticmethod
    def _validate_response(
        data: dict[str, Any],
    ) -> None:
        """
        Validate the provider response.
        """

        if "response" not in data:

            raise LLMResponseError(
                "LLM returned an invalid response."
            )

    @staticmethod
    def _clean_json_response(
        text: str,
    ) -> str:
        """
        Remove Markdown fences from JSON responses.
        """

        if not text.startswith("```"):

            return text

        lines = text.splitlines()

        if lines:

            lines = lines[1:]

        if lines and lines[-1].strip() == "```":

            lines = lines[:-1]

        return "\n".join(lines).strip()

    def generate(
        self,
        system: str,
        prompt: str,
        temperature: float | None = None,
    ) -> str:
        """
        Generate plain text from the configured LLM.
        """

        if self.provider not in SUPPORTED_PROVIDERS:

            raise LLMResponseError(
                f"Unsupported LLM provider '{self.provider}'."
            )

        if temperature is None:

            temperature = self.temperature

        payload = self._build_payload(
            system=system,
            prompt=prompt,
            temperature=temperature,
        )

        self._log_request(
            temperature=temperature,
            prompt=prompt,
        )

        data = self._send_request(
            payload,
        )

        self._log_response(
            data,
        )

        self._validate_response(
            data,
        )

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

        text = self._clean_json_response(
            text,
        )

        LOGGER.info("=" * 70)
        LOGGER.info("JSON TO PARSE")
        LOGGER.info("=" * 70)
        LOGGER.info(text)
        LOGGER.info("=" * 70)

        try:

            return json.loads(text)

        except json.JSONDecodeError as ex:

            LOGGER.exception(
                "LLM returned invalid JSON."
            )

            raise LLMResponseError(
                "LLM did not return valid JSON."
            ) from ex