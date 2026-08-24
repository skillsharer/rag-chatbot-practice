from dataclasses import dataclass
from typing import Any

@dataclass
class BackendConnector:
    backendInstance = None

    def __init__(self, backend: Any):
        self.backend = backend
        self.last_visited_nodes = []
    
    def chat(self, message: str, thread_id: str) -> str:
        """
        Send a message to the LangGraph backend.
        """
        self.backend.visited_nodes = []

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
        self.last_visited_nodes = self.backend.visited_nodes

        return result["answer"]

    def get_execution_graph(self) -> str:
        nodes = ["START"] + self.last_visited_nodes + ["END"]

        edges = "\n".join(
            f'"{nodes[i]}" -> "{nodes[i + 1]}"'
            for i in range(len(nodes) - 1)
        )

        return f"""
        digraph {{
            rankdir=TB
            node [shape=box, style=rounded]
            {edges}
        }}
        """

    def get_retrieved_documents(self):
        return self.backend.retrieved_documents
    
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