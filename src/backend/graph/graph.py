from langgraph.graph import START, END, StateGraph
from langchain_core.utils.json import parse_json_markdown
from src.backend.state import SystemState
from src.backend.prompts import INTENTPROMPT, PLAN_PROMPT, SUMMARY_PROMPT
from src.backend.ollama import OllamaConnector
from src.backend.data.db import VectorDatabase
from src.backend.data.embed import Embedder

class BackendStateMachine:
    def __init__(self):
        self.ollama_connector = OllamaConnector()
        self.vector_db = VectorDatabase()
        self.sentence_embedder = Embedder()
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

        builder.add_node("intent_classification", self.intent_classification)
        builder.add_node("plan_task", self.plan_task)
        builder.add_node("rag", self.rag_graph)
        builder.add_node("tool",self.tool_graph)
        builder.add_node("summarize", self.summarize)

        builder.add_edge(START, "intent_classification")
        builder.add_edge("intent_classification", "plan_task")
        builder.add_conditional_edges("plan_task", self.route_task)
        builder.add_edge("rag", "summarize")
        builder.add_edge("tool", "summarize")
        builder.add_edge("summarize", END)

        self.graph = builder.compile()


    def intent_classification(self, state: SystemState):
        messages = [
            {
                "role": "system",
                "content": INTENTPROMPT
            }
        ]
        messages.extend(state.get("messages", []))
        messages.append(
            {
                "role": "user",
                "content": state['user_query']
            }
        )
        response = self.ollama_connector.chat(messages=messages)
        response_json = parse_json_markdown(response)
        return {
            "refined_query": response_json["refined_query"], 
            "refinement_needed": response_json["refinement_needed"],
            "clarification_needed": response_json["clarification_needed"], 
            "clarification_question": response_json["clarification_question"]
            }

    def plan_task(self, state: SystemState):
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
        return {"plan": response_json["strategy"]}


    def route_task(self, state: SystemState):
        if state["plan"] == "RAG":
            return "rag"
        elif state["plan"] == "TOOL":
            return "tool"
        return "summarize"


    def summarize(self, state: SystemState):
        context = state.get("retrieved_documents", [])
        tool_result = state.get("tool_result", "")
        messages = [{
            "role": "system",
            "content": SUMMARY_PROMPT
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
            """
        }
        ]
        response = self.ollama_connector.chat(messages=messages)
        return {"answer": response}


    def retrieve(self, state: SystemState):
        query_vector = self.sentence_embedder.embed(state["refined_query"])
        top_k_answers = self.vector_db.retrieve_top_k(query_vector=query_vector)
        return {"retrieved_documents": top_k_answers}

    def rerank(self, state: SystemState):
        return {"retrieved_documents": state["retrieved_documents"]}

    def select_tool(self, state: SystemState):
        return {
            "tool_result": "No tool implemented yet."
        }

    def execute_tool(self, state: SystemState):
        return {}


if __name__ == "__main__":
    backend_state_machine = BackendStateMachine()
    result = backend_state_machine.graph.invoke({
        "user_query": "Hi, is there any medicine which helps for my headache?"
    })

    print(result)