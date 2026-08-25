import os
from pathlib import Path
from dotenv import load_dotenv

WORKSPACE_PATH = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(WORKSPACE_PATH,".env"))

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
MAX_NUM_OF_AGENT_STEPS = int(os.getenv("MAX_NUM_OF_AGENT_STEPS", 5))
DATABASE_PATH = os.path.join(WORKSPACE_PATH, os.getenv("DATABASE_PATH", "database"))
SNAPSHOT_PATH = os.path.join(WORKSPACE_PATH, os.getenv("SNAPSHOT_PATH", "tmp/db.npy"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
TOP_K = int(os.getenv("TOP_K", 10))
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
NUM_REQUESTS = int(os.getenv("NUM_REQUESTS", 50))
WARMUP_REQUESTS = int(os.getenv("WARMUP_REQUESTS", 3))