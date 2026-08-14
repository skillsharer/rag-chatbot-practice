from state import SystemState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

def intent_classification():
    pass

def plan_task():
    pass

def route_task():
    pass

def summarize():
    pass

def retrieve():
    pass

def rerank():
    pass

def select_tool():
    pass

def execute_tool():
    pass



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
