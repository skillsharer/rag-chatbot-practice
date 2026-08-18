import requests
from dataclasses import dataclass
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL


@dataclass
class OllamaConnector:
    def __init__(self):
        self.host = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL

    def chat(self, messages):
        """
        Send chat messages to Ollama and return the assistant response.
        """
        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()["message"]["content"]