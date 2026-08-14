import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", default="gemma3:4b"),
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", default="http://localhost:11434/")

 