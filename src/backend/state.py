from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class SystemState(TypedDict):
    user_query: str
    messages: Annotated[list, add_messages]
    refined_query: str
    clarification_needed: bool
    clarification_question: Optional[str]
    plan: str
    retrieved_documents: list
    tool_result: str
    answer: str