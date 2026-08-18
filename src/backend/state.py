from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class SystemState(TypedDict):
    messages: Annotated[list, add_messages]
    refined_query: str
    plan: str
    retrieved_documents: list
    tool_result: str
    answer: str