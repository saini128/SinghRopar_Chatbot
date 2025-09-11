import os
import requests
from models.chat_models import GroqResponse

GROQ_API = os.getenv("GROQ_API")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Keep answers concise and to the point and below 400 tokens."
)


def getGroqResponse(prompt: str) -> GroqResponse:
    headers = {
        "Authorization": f"Bearer {GROQ_API}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "temperature": 0.7,
        "max_tokens": 500,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(GROQ_URL, headers=headers, json=data)
    raw = response.json()
    return GroqResponse.from_api(raw)