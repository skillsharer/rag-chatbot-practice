from sentence_transformers import SentenceTransformer
from config import SENTENCE_TRANSFORMER_MODEL
from db import VectorDatabase

class Embedder:
    def __init__(self):
        self.embedder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        self.db = VectorDatabase()

    def embed(self, text):
        """
        Embedding and uploading to the vector database the chunks.
        """
        vector = self.embedder.encode(text)
        self.db.add(vector=vector, text=text)

    def query(self, text):
        """
        Embed the query vector and retrieve the top k results which are similar to the query vector based on cosine similarity.
        """
        vector = self.embedder.encode(text)
        results = self.db.retrieve_top_k(vector)
        return results
