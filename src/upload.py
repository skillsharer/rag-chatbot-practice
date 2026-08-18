import os
import logging
from src.config import DATABASE_PATH, SNAPSHOT_PATH
from src.backend.data.data_preprocess import DataPreprocessor
from src.backend.data.db import VectorDatabase
from src.backend.data.embed import Embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing...")
data_preprocessor = DataPreprocessor()
vector_db = VectorDatabase()
sentence_embedder = Embedder()
logger.info("Initializing finished")

# Load pdfs and chunkify
data_files = [f for f in os.listdir(DATABASE_PATH) if f.endswith(".pdf")]
total = len(data_files)
for idx, data_file in enumerate(data_files, start=1):
    logger.info(f"Processing {idx}/{total}")
    file_path = os.path.join(DATABASE_PATH, data_file)
    text_data = data_preprocessor.load_pdf(file_path)
    chunks = data_preprocessor.chunkify(text_data=text_data)
    # Embed and upload
    for chunk in chunks:
        embedded_vector = sentence_embedder.embed(text=chunk)
        vector_db.add(vector=embedded_vector, text=chunk)


# Make a snapshot
logger.info(f"Creating snapshot to: {SNAPSHOT_PATH}")
vector_db.create_snapshot(output_path=SNAPSHOT_PATH)
