from pathlib import Path

from shared.mcp_client import MCPClient


class ExecutiveProducer:

    def __init__(self):

        self.llm = MCPClient()

        prompt_file = (
            Path(__file__).parent /
            "prompt.md"
        )

        self.system_prompt = prompt_file.read_text(
            encoding="utf-8"
        )

    def run(self, user_request: str):

        return self.llm.generate_json(

            system=self.system_prompt,

            prompt=user_request,

            temperature=0.4

        )