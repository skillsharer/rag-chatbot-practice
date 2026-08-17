from dataclasses import dataclass
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from ollama import Client


@dataclass
class OllamaConnector:
    def __init__(self):
        self.host = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.client = Client(host=self.host)

    def chat(self, messages):
        """
        Send chat messages to Ollama and return the assistant response.
        """
        response = self.client.chat(model=self.model, messages=messages)
        
        return response["message"]["content"]