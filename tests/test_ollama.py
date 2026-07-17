import requests

payload = {
    "model": "gemma4:12b",   # use exactly the model name from config.yaml
    "prompt": "Say hello.",
    "stream": False
}

response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json=payload,
    timeout=300
)

print("Status:", response.status_code)
print()
print(response.text)