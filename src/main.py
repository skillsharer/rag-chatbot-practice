from ui.connector import BackendConnector
from ui.ui import UserInterface
from backend import graph

connector = BackendConnector.create(graph)
streamlit_ui = UserInterface(page_title="RAG Chat Practice by Bence Farkas", layout="wide", connector=connector)
streamlit_ui.run()
