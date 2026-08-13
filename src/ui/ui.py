import streamlit as st

class UserInterface:

    def __init__(self, page_title, layout, connector):
        # Initial page settings
        st.set_page_config(
            page_title=page_title,
            layout=layout,
        )

        self.connector = connector
        self.chat_column, self.graph_column = st.columns([2, 1])

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "thread_id" not in st.session_state:
            st.session_state.thread_id = "streamlit-session"


    def run(self):
        # UI columns
        with self.chat_column:
            st.subheader("Chat")

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_message = st.chat_input("Ask something...")

            if user_message:
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": user_message,
                    }
                )

                with st.chat_message("user"):
                    st.markdown(user_message)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = self.connector.chat(
                            message=user_message,
                            thread_id=st.session_state.thread_id,
                        )

                    st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

        with self.graph_column:
            st.subheader("Graph")

            try:
                graph_png = self.connector.get_graph_png()
                st.image(graph_png, use_container_width=True)
            except Exception as exc:
                st.info(f"Graph visualization unavailable: {exc}")

            st.divider()

            if st.button("Clear chat"):
                self.connector.delete_chat(st.session_state.thread_id)
                st.session_state.messages = []
                st.rerun()