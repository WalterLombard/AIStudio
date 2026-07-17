import json
from pathlib import Path

from shared.mcp_client import MCPClient


class ScriptWriter:

    def __init__(self):

        self.llm = MCPClient()

        prompt_file = Path(__file__).parent / "prompt.md"

        self.system_prompt = prompt_file.read_text(
            encoding="utf-8"
        )

    def run(
        self,
        production_brief: dict,
        research: dict
    ):

        payload = {

    "title": production_brief["title"],

    "scene_count": production_brief["scene_count"],

    "tone": production_brief["tone"],

    "research_summary": research["summary"],

    "facts": research["facts"]

}