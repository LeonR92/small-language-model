import os

import requests
from dotenv import load_dotenv

load_dotenv()


def talk_to_ai(
    user_question: str, ai_model: str, system_prompt: str, temperature: float
) -> str:
    api_key = os.getenv("MISTRAL_API_KEY")
    url = "https://api.mistral.ai/v1/chat/completions"
    payload = {
        "model": f"{ai_model}",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"]
