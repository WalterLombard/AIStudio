import requests

from shared.config import config
from shared.logger import get_logger
from shared.parsers import JSONParser


class MCPClient:

    def __init__(self):
        self.logger = get_logger("MCPClient")
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = config.models.llm.model

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
    ) -> str:

        if system.strip():
            prompt = f"""{system}

--------------------------------------------

USER REQUEST

{prompt}
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 4096
            }
        }

        self.logger.info(f"Calling {self.model}")

        print("\n================ REQUEST =================\n")
        print(f"Model         : {self.model}")
        print(f"Prompt Length : {len(prompt)} characters")
        print("\n==========================================\n")

        response = requests.post(
            self.url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        result = response.json()

        print("\n================ OLLAMA RESPONSE =================\n")
        print(f"Model         : {result.get('model')}")
        print(f"Done          : {result.get('done')}")
        print(f"Done Reason   : {result.get('done_reason')}")
        print(f"Prompt Tokens : {result.get('prompt_eval_count')}")
        print(f"Output Tokens : {result.get('eval_count')}")
        print(f"Total Time(ns): {result.get('total_duration')}")
        print()

        response_text = result.get("response", "")

        if response_text:
            print(response_text)
        else:
            print("<EMPTY RESPONSE>")

        print("\n==================================================\n")

        #
        # Detect if Ollama stopped because it hit the output limit
        #

        if result.get("done_reason") == "length":
            raise RuntimeError(
                f"""
Gemma stopped because it reached num_predict.

done_reason : {result.get("done_reason")}
response len: {len(response_text)}

Increase num_predict or reduce the prompt.
"""
            )

        return response_text

    def generate_json(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.4,
    ):

        text = self.generate(
            prompt=prompt,
            system=system,
            temperature=temperature,
        )

        print("\n======================================================================")
        print("RAW LLM RESPONSE")
        print("======================================================================")

        print(text)

        print("======================================================================")

        return JSONParser.parse(text)