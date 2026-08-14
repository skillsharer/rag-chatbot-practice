import numpy as np
from config import TOP_K


class VectorDatabase:
    def __init__(self):
        self.db = []
        self.top_k = TOP_K

    def retrieve_top_k(self, query_vector):
        """
        Retrieve top k similar texts from the database.
        """
        scored = [
            (
                idx,
                entry["text"],
                self.compare(query_vector, entry["vector"]),
            )
            for idx, entry in enumerate(self.db)
        ]

        scored.sort(key=lambda x: x[2], reverse=True)

        return scored[:self.top_k]

    def compare(self, query_vector, db_vector):
        """
        Compare two vectors based on cosine similarity.
        """
        query_vector = np.array(query_vector)
        db_vector = np.array(db_vector)

        denominator = (
            np.linalg.norm(query_vector)
            * np.linalg.norm(db_vector)
        )

        if denominator == 0:
            return 0.0

        return np.dot(query_vector, db_vector) / denominator

    def add(self, vector, text):
        """
        Add vector and corresponding text to the database.
        """
        self.db.append(
            {
                "vector": np.array(vector),
                "text": text,
            }
        )

    def delete(self, idx):
        """
        Delete entry from the database.
        """
        del self.db[idx]

    def create_snapshot(self, output_path):
        """
        Save the current vector database to disk.
        """
        np.save(output_path, self.db)


    def load_snapshot(self, snapshot_path):
        """
        Load the vector database from disk.
        """
        self.db = np.load(snapshot_path, allow_pickle=True).tolist()