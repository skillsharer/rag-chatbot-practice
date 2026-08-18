from sentence_transformers import SentenceTransformer
from src.config import SENTENCE_TRANSFORMER_MODEL

class Embedder:
    def __init__(self):
        self.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)

    def embed(self, text):
        """
        Embedding and uploading to the vector database the chunks.
        """
        vector = self.embedder.encode(text, show_progress_bar=False)
        return vector
