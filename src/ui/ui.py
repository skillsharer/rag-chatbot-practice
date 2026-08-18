import streamlit as st
import uuid

class UserInterface:

    def __init__(self, page_title, layout, connector):
        st.set_page_config(
            page_title=page_title,
            layout=layout,
        )

        self.connector = connector

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "thread_id" not in st.session_state:
            st.session_state.thread_id = str(uuid.uuid4())

    def run(self):
        chat_column, graph_column = st.columns([2, 1])

        with chat_column:
            st.subheader("Medication assistant")
            st.caption("Answers are grounded in medication information leaflets.")

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with graph_column:
            st.subheader("Graph")
            graph_placeholder = st.empty()

            graph_placeholder.graphviz_chart(
                self.connector.get_execution_graph()
            )

        with st.bottom:
            user_message = st.chat_input("Ask about a medication...")

            if st.button("Clear chat"):
                self.connector.delete_chat(st.session_state.thread_id)
                st.session_state.messages = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()

        if user_message:
            st.session_state.messages.append({
                "role": "user",
                "content": user_message,
            })

            with chat_column:
                with st.chat_message("user"):
                    st.markdown(user_message)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = self.connector.chat(
                            message=user_message,
                            thread_id=st.session_state.thread_id,
                        )
                        graph_placeholder.graphviz_chart(self.connector.get_execution_graph())

                    st.markdown(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
            })