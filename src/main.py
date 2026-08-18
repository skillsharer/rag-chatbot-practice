import streamlit as st
from src.ui.connector import BackendConnector
from src.ui.ui import UserInterface
from src.backend.graph.graph import BackendStateMachine

@st.cache_resource
def get_backend():
    return BackendStateMachine()


backend = get_backend()
connector = BackendConnector(backend)
streamlit_ui = UserInterface(page_title="RAG Chat Practice by Bence Farkas", layout="wide", connector=connector)
streamlit_ui.run()
