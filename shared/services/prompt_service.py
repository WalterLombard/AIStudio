"""
AIStudio Prompt Service

Responsible for locating and loading prompt files used by every AI agent.

Each agent simply calls:

    PromptService.load_prompt(__file__)

The service automatically locates prompt.md in the same folder.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path

from shared.exceptions import AIStudioError
from shared.logger import get_logger


LOGGER = get_logger("PromptService")


class PromptService:
    """
    Loads prompt files for AI agents.
    """

    PROMPT_FILENAME = "prompt.md"

    @staticmethod
    def load_prompt(
        agent_file: str,
    ) -> str:
        """
        Load the prompt file associated with an agent.

        Parameters
        ----------
        agent_file
            The __file__ value from the calling agent.

        Returns
        -------
        str
            The prompt contents.

        Raises
        ------
        AIStudioError
            If the prompt file cannot be found.
        """

        prompt_file = (
            Path(agent_file).parent
            / PromptService.PROMPT_FILENAME
        )

        LOGGER.info(
            "Loading prompt: %s",
            prompt_file,
        )

        if not prompt_file.exists():

            raise AIStudioError(
                f"Prompt file does not exist:\n{prompt_file}"
            )

        prompt = prompt_file.read_text(
            encoding="utf-8",
        )

        LOGGER.info(
            "Prompt loaded successfully."
        )

        return prompt