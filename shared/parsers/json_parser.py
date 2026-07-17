import json


def extract_first_json(text: str) -> str:
    """
    Extracts the first complete JSON object from a string.

    This works even if the LLM appends explanations,
    markdown or a second JSON object afterwards.
    """

    start = text.find("{")

    if start == -1:
        return text

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

        if c == "{":
            depth += 1

        elif c == "}":
            depth -= 1

            if depth == 0:
                return text[start:i + 1]

    return text


class JSONParser:

    @staticmethod
    def parse(text: str):

        if not text:
            raise ValueError("LLM returned an empty response.")

        #
        # Remove markdown
        #

        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        #
        # Keep only the FIRST complete JSON object
        #

        text = extract_first_json(text)

        try:
            return json.loads(text)

        except json.JSONDecodeError as ex:

            print("\n================ RAW LLM OUTPUT ================\n")
            print(text)
            print("\n================================================\n")

            raise ValueError(
                f"Gemma returned invalid JSON.\n{ex}"
            )