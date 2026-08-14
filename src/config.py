import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", default="gemma3:4b"),
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", default="http://localhost:11434/")

DATABASE_PATH = os.getenv("DATABASE_PATH", default="../database")
SNAPSHOT_PATH = os.getenv("SNAPSHOT_PATH", default="./tmp/db.npy")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", default=300))
TOP_K = int(os.getenv("TOP_K", default=10))
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", default="all-MiniLM-L6-v2")
