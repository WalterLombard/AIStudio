import json
from pathlib import Path

from shared.mcp_client import MCPClient


class ResearchAgent:

    def __init__(self):

        self.llm = MCPClient()

        prompt_file = Path(__file__).parent / "prompt.md"

        self.system_prompt = prompt_file.read_text(
            encoding="utf-8"
        )

    def run(self, production_brief: dict):

        prompt = json.dumps(
            production_brief,
            indent=4
        )

        return self.llm.generate_json(

            system=self.system_prompt,

            prompt=prompt,

            temperature=0.2

        )