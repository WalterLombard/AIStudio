import requests

payload = {
    "model": "gemma4:12b",  # exact model match from Modelfile and config
    "prompt": "Say hello.",
    "stream": False,
}

try:
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json=payload,
        timeout=300,
    )

    print("Status:", response.status_code)
    print()
    print(response.text)

except requests.RequestException as ex:
    print(f"Failed to connect to local Ollama instance: {ex}")