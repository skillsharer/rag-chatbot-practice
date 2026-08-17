from typing import TypedDict, Optional

class SystemState(TypedDict):
    user_query: str
    messages: list[dict]
    refined_query: str
    clarification_needed: bool
    clarification_question: Optional[str]
    plan: str
    retrieved_documents: list
    tool_result: str
    answer: str