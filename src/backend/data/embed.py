from sentence_transformers import SentenceTransformer
from config import SENTENCE_TRANSFORMER_MODEL

class Embedder:
    def __init__(self, vector_database):
        self.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        self.db = vector_database

    def embed(self, text):
        """
        Embedding and uploading to the vector database the chunks.
        """
        vector = self.embedder.encode(text)
        return vector
