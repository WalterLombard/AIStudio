"""
AIStudio JSON Parser

Utility for extracting and parsing raw JSON objects/arrays from LLM text responses.

Author : AIStudio
"""

from __future__ import annotations

import json


def extract_first_json(text: str) -> str:
    """
    Extracts the first complete JSON object ({...}) or JSON array ([...]) from a string.

    This works even if the LLM appends explanations, markdown formatting,
    or additional JSON blocks afterwards.
    """
    obj_start = text.find("{")
    arr_start = text.find("[")

    # Determine which comes first
    if obj_start == -1 and arr_start == -1:
        return text

    if obj_start != -1 and (arr_start == -1 or obj_start < arr_start):
        start = obj_start
        open_char, close_char = "{", "}"
    else:
        start = arr_start
        open_char, close_char = "[", "]"

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        c = text[i]

        if escape:
            escape = False
            continue

        if c == "\\":
            escape = True
            continue

        if c == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1

            if depth == 0:
                return text[start : i + 1]

    return text


class JSONParser:
    """
    Utility class for safely parsing JSON payloads from LLM outputs.
    """

    @staticmethod
    def parse(text: str) -> dict | list:
        if not text or not text.strip():
            raise ValueError("LLM returned an empty response.")

        # Clean common markdown fences (case-insensitive handling)
        text = text.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

        # Extract the first valid structural JSON payload
        text = extract_first_json(text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as ex:
            print("\n================ RAW LLM OUTPUT ================\n")
            print(text)
            print("\n================================================\n")
            raise ValueError(f"LLM returned invalid JSON.\n{ex}")