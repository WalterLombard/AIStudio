import json
from pathlib import Path

from shared.mcp_client import MCPClient


class OutlineAgent:

    def __init__(self):

        self.llm = MCPClient()

        prompt_file = Path(__file__).parent / "prompt.md"

        self.system_prompt = prompt_file.read_text(
            encoding="utf-8"
        )

    def run(self, production_brief: dict, research: dict):
        payload = {
            "title": production_brief["title"],
            "duration_minutes": production_brief["duration_minutes"],
            "audience": production_brief["audience"],
            "tone": production_brief["tone"],
            "summary": research["summary"],
            "facts": research["facts"],
            "timeline": research["timeline"]
        }

        return self.llm.generate_json(
            system=self.system_prompt,
            prompt=json.dumps(payload, indent=4),
            temperature=0.1
        )