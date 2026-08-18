import os
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.utils.json import parse_json_markdown
from langchain_core.messages import convert_to_openai_messages
from src.config import SNAPSHOT_PATH, DATABASE_PATH
from src.backend.state import SystemState
from src.backend.prompts import REFINEMENT_PROMPT, PLAN_PROMPT, SUMMARY_PROMPT, TOOL_PROMPT
from src.backend.ollama import OllamaConnector
from src.backend.data.db import VectorDatabase
from src.backend.data.embed import Embedder
from backend.tools.wiki_search import WikipediaSearch

class BackendStateMachine:
    def __init__(self):
        self.ollama_connector = OllamaConnector()
        self.vector_db = VectorDatabase()
        self.vector_db.load_snapshot(SNAPSHOT_PATH)
        self.sentence_embedder = Embedder()
        self.checkpointer = InMemorySaver()
        self.wiki_search = WikipediaSearch()
        self.visited_nodes = []
        self.last_retrieved_documents = []
        self.build_graph()

    def build_graph(self):
        # RAG GRAPH:
        rag_builder = StateGraph(SystemState)

        rag_builder.add_node("retrieve", self.retrieve)
        rag_builder.add_node("rerank", self.rerank)

        rag_builder.add_edge(START, "retrieve")
        rag_builder.add_edge("retrieve", "rerank")
        rag_builder.add_edge("rerank", END)

        self.rag_graph = rag_builder.compile()

        # TOOL GRAPH:
        tool_builder = StateGraph(SystemState)

        tool_builder.add_node("select_tool", self.select_tool)
        tool_builder.add_node("execute_tool", self.execute_tool)

        tool_builder.add_edge(START, "select_tool")
        tool_builder.add_edge("select_tool", "execute_tool")
        tool_builder.add_edge("execute_tool", END)

        self.tool_graph = tool_builder.compile()

        # FINAL GRAPH:

        builder = StateGraph(SystemState)

        builder.add_node("user_query_refinement", self.user_query_refinement)
        builder.add_node("plan_task", self.plan_task)
        builder.add_node("rag", self.rag_graph)
        builder.add_node("tool",self.tool_graph)
        builder.add_node("summarize", self.summarize)

        builder.add_edge(START, "user_query_refinement")
        builder.add_edge("user_query_refinement", "plan_task")
        builder.add_conditional_edges("plan_task", self.route_task)
        builder.add_edge("rag", "summarize")
        builder.add_edge("tool", "summarize")
        builder.add_edge("summarize", END)

        self.graph = builder.compile(checkpointer=self.checkpointer)


    def user_query_refinement(self, state: SystemState):
        self.visited_nodes.append("user_query_refinement")
        self.last_retrieved_documents = []

        messages = [
            {
                "role": "system",
                "content": REFINEMENT_PROMPT,
            }
        ]

        history = convert_to_openai_messages(
            state.get("messages", [])
        )
        messages.extend(history)

        response = self.ollama_connector.chat(messages=messages)
        response_json = parse_json_markdown(response)

        return {
            "refined_query": response_json.get("refined_query", "")
        }

    def plan_task(self, state: SystemState):
        self.visited_nodes.append("plan_task")
        messages = [
                {
                    "role": "system",
                    "content": PLAN_PROMPT
                },
                {
                    "role": "user",
                    "content": state['refined_query']
                }
            ]
        response = self.ollama_connector.chat(messages=messages)
        response_json = parse_json_markdown(response)
        return {"plan": response_json.get("plan", "SIMPLE")}


    def route_task(self, state: SystemState):
        if state["plan"] == "RAG":
            return "rag"
        elif state["plan"] == "TOOL":
            return "tool"
        return "summarize"


    def summarize(self, state: SystemState):
        self.visited_nodes.append("summarize")
        context = state.get("retrieved_documents", [])
        tool_result = state.get("tool_result", "")

        messages = [
            {
                "role": "system",
                "content": SUMMARY_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
                Query:
                {state["refined_query"]}

                Retrieved context:
                {context}

                Tool result:
                {tool_result}
                """,
            },
        ]

        response = self.ollama_connector.chat(messages=messages)

        return {
            "answer": response,
            "messages": [
                {
                    "role": "assistant",
                    "content": response,
                }
            ],
            "retrieved_documents": []
        }


    def retrieve(self, state: SystemState):
        self.visited_nodes.append("retrieve")
        query_vector = self.sentence_embedder.embed(state["refined_query"])
        top_k_answers = self.vector_db.retrieve_top_k(query_vector=query_vector)
        return {"retrieved_documents": top_k_answers}

    def rerank(self, state: SystemState):
        self.visited_nodes.append("rerank")

        reranked_documents = state["retrieved_documents"]
        self.last_retrieved_documents = reranked_documents

        return {"retrieved_documents": reranked_documents}

    def select_tool(self, state: SystemState):
        self.visited_nodes.append("select_tool")

        messages = [
            {
                "role": "system",
                "content": TOOL_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
                User query:
                    {state["refined_query"]}
                """,
            },
        ]
        response = self.ollama_connector.chat(messages=messages)
        response = parse_json_markdown(response)
        return {"tool": response.get("tool", ""), "tool_args": response.get("tool_args", "")}

    def execute_tool(self, state: SystemState):
        self.visited_nodes.append("execute_tool")
        if state.get("tool", "") == "wikipedia":
            tool_result = self.wiki_search.search(state["tool_args"])
        else:
            tool_result = [f for f in os.listdir(DATABASE_PATH) if f.endswith(".pdf")]
        return {"tool_result": tool_result}

    def delete_chat(self, thread_id: str):
        self.backend.checkpointer.delete_thread(thread_id)


if __name__ == "__main__":
    backend_state_machine = BackendStateMachine()
    result = backend_state_machine.graph.invoke({
        "user_query": "Hi, is there any medicine which helps for my headache?"
    })

    print(result)