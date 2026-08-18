import pymupdf
from src.config import CHUNK_SIZE

class DataPreprocessor:
    def __init__(self):
        self.chunk_size = CHUNK_SIZE

    def load_pdf(self, file_path):
        """
        Loads pdf file and simply read text from it.
        """
        pdf_text_data = ""
        with pymupdf.open(file_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text("text").lower()
                pdf_text_data += page_text + " "

        return pdf_text_data


    def chunkify(self, text_data):
        """
        Chunkify based on text size not token size.
        """
        chunks =  [text_data[i:i + self.chunk_size] for i in range(0, len(text_data), self.chunk_size)]
        return chunks