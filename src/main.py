from src.ui.connector import BackendConnector
from src.ui.ui import UserInterface
from src.backend.graph.graph import BackendStateMachine

backend_state_machine = BackendStateMachine()
connector = BackendConnector(backend_state_machine)
streamlit_ui = UserInterface(page_title="RAG Chat Practice by Bence Farkas", layout="wide", connector=connector)
streamlit_ui.run()
