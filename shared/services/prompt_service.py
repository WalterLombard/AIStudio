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

    @staticmethod
    def load_prompt(agent_file: str) -> str:
        """
        Load the prompt.md located beside an agent.py file.

        Parameters
        ----------
        agent_file
            Usually __file__ from the calling agent.

        Returns
        -------
        str
            Prompt contents.
        """

        prompt_file = Path(agent_file).parent / "prompt.md"

        LOGGER.info(
            "Loading prompt: %s",
            prompt_file,
        )

        if not prompt_file.exists():

            raise AIStudioError(
                f"Prompt file does not exist:\n{prompt_file}"
            )

        return prompt_file.read_text(
            encoding="utf-8"
        )