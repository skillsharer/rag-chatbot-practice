from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class CurrentTask(TypedDict):
    task_id: int
    task: str
    type: str
    tool: str | None
    tool_args: dict | None

class SystemState(TypedDict):
    messages: Annotated[list, add_messages]
    action: str | None
    refined_query: str
    plan: list[CurrentTask]
    completed_tasks: list
    current_task: CurrentTask | None
    retrieved_documents: list
    steps: int
    answer: str