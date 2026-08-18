from dataclasses import dataclass
from typing import Any

@dataclass
class BackendConnector:
    backendInstance = None

    def __init__(self, backend: Any):
        self.backend = backend
    
    def chat(self, message: str, thread_id: str) -> str:
        """
        Send a message to the LangGraph backend.
        """
        result = self.backend.graph.invoke(
            {
                "user_query": message,
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            },
        )
        return result["answer"]

    def get_graph_png(self) -> bytes:
        """
        Return the LangGraph graph as PNG bytes.
        """
        return self.backend.graph.get_graph().draw_mermaid_png()

    def delete_chat(self, thread_id: str):
        """
        Deletes chat history if user presses clear conversation button.
        """
        self.backend.checkpointer.delete_thread(thread_id)


    @classmethod
    def create(cls, graph):
        if (cls.backendInstance == None):
            cls.backendInstance = BackendConnector(graph)

        return cls.backendInstance