import os
from config import DATABASE_PATH, SNAPSHOT_PATH
from backend.data.data_preprocess import DataPreprocessor
from backend.data.db import VectorDatabase
from backend.data.embed import Embedder


data_preprocessor = DataPreprocessor()
vector_db = VectorDatabase()
sentence_embedder = Embedder()

# Load pdfs and chunkify
data_files = os.listdir(DATABASE_PATH)
for data_file in data_files:
    text_data = data_preprocessor.load_pdf(data_file)
    chunks = data_preprocessor.chunkify(text_data=text_data)
    # Embed and upload
    for chunk in chunks:
        embedded_vector = sentence_embedder.embed(text=chunk)
        vector_db.add(vector=embedded_vector, text=chunk)


# Make a snapshot
vector_db.create_snapshot(output_path=SNAPSHOT_PATH)
