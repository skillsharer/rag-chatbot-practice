import json
from langgraph.graph import START, END, StateGraph
from langchain_core.utils.json import parse_json_markdown
from src.backend.state import SystemState
from src.backend.prompts import INTENTPROMPT, PLAN_PROMPT, SUMMARY_PROMPT
from src.backend.ollama import OllamaConnector
from src.backend.data.db import VectorDatabase
from src.backend.data.embed import Embedder

def intent_classification(state: SystemState):
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
    response = ollama_connector.chat(messages=messages)
    response_json = parse_json_markdown(response)
    return {
        "refined_query": response_json["refined_query"], 
        "refinement_needed": response_json["refinement_needed"],
        "clarification_needed": response_json["clarification_needed"], 
        "clarification_question": response_json["clarification_question"]
        }

def plan_task(state: SystemState):
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
    response = ollama_connector.chat(messages=messages)
    response_json = parse_json_markdown(response)
    return {"plan": response_json["strategy"]}


def route_task(state: SystemState):
    if state["plan"] == "RAG":
        return "retrieve"
    elif state["plan"] == "TOOL":
        return "select_tool"
    return "summarize"


def summarize(state: SystemState):
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
    response = ollama_connector.chat(messages=messages)
    return {"answer": response}


def retrieve(state: SystemState):
    query_vector = sentence_embedder.embed(state["refined_query"])
    top_k_answers = vector_db.retrieve_top_k(query_vector=query_vector)
    return {"retrieved_documents": top_k_answers}

def rerank(state: SystemState):
    return {"retrieved_documents": state["retrieved_documents"]}

def select_tool(state: SystemState):
    return {
        "tool_result": "No tool implemented yet."
    }

def execute_tool(state: SystemState):
    return {}

ollama_connector = OllamaConnector()
vector_db = VectorDatabase()
sentence_embedder = Embedder()

# RAG GRAPH:
rag_builder = StateGraph(SystemState)

rag_builder.add_node("retrieve", retrieve)
rag_builder.add_node("rerank", rerank)

rag_builder.add_edge(START, "retrieve")
rag_builder.add_edge("retrieve", "rerank")
rag_builder.add_edge("rerank", END)

rag_graph = rag_builder.compile()

# TOOL GRAPH:
tool_builder = StateGraph(SystemState)

tool_builder.add_node("select_tool", select_tool)
tool_builder.add_node("execute_tool", execute_tool)

tool_builder.add_edge(START, "select_tool")
tool_builder.add_edge("select_tool", "execute_tool")
tool_builder.add_edge("execute_tool", END)

tool_graph = tool_builder.compile()

# FINAL GRAPH:

builder = StateGraph(SystemState)

builder.add_node("intent_classification", intent_classification)
builder.add_node("plan_task", plan_task)
builder.add_node("rag", rag_graph)
builder.add_node("tool", tool_graph)
builder.add_node("summarize", summarize)

builder.add_edge(START, "intent_classification")
builder.add_edge("intent_classification", "plan_task")
builder.add_conditional_edges("plan_task", route_task)
builder.add_edge("rag", "summarize")
builder.add_edge("tool", "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "user_query": "Hi, what do you mean by it?"
    })

    print(result)