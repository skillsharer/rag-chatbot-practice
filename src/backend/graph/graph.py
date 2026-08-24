import logging
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.utils.json import parse_json_markdown
from langchain_core.messages import convert_to_openai_messages
from src.config import SNAPSHOT_PATH, MAX_NUM_OF_AGENT_STEPS
from src.backend.state import SystemState
from src.backend.prompts import refinement_prompt, agent_prompt, review_prompt, summary_prompt
from src.backend.ollama import OllamaConnector
from src.backend.data.db import VectorDatabase
from src.backend.data.embed import Embedder
from src.backend.tools.stock_price import get_stock_price
from src.backend.tools.financial_metric import get_latest_financial_metric
from src.backend.utils.latency import measure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendStateMachine:
    def __init__(self):
        self.ollama_connector = OllamaConnector()
        self.vector_db = VectorDatabase()
        self.vector_db.load_snapshot(SNAPSHOT_PATH)
        self.sentence_embedder = Embedder()
        self.checkpointer = InMemorySaver()
        self.visited_nodes = []
        self.retrieved_documents = []
        self.build_graph()

    @measure
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

        tool_builder.add_node("tool", self.tool)

        tool_builder.add_edge(START, "tool")
        tool_builder.add_edge("tool", END)

        self.tool_graph = tool_builder.compile()

        # FINAL GRAPH:
        builder = StateGraph(SystemState)

        builder.add_node("user_query_refinement", self.user_query_refinement)
        builder.add_node("agent", self.agent)
        builder.add_node("select_next_task", self.select_next_task)
        builder.add_node("rag", self.rag_graph)
        builder.add_node("tool", self.tool_graph)
        builder.add_node("summarize", self.summarize)

        builder.add_edge(START, "user_query_refinement")
        builder.add_conditional_edges("user_query_refinement", self.route_query)
        builder.add_conditional_edges("agent", self.route_agent)
        builder.add_conditional_edges("select_next_task", self.route_task)
        builder.add_edge("rag", "select_next_task")
        builder.add_edge("tool", "select_next_task")

        builder.add_edge("summarize", END)
        self.graph = builder.compile(checkpointer=self.checkpointer)

    @measure
    def user_query_refinement(self, state: SystemState):
        """
        Refining user query and delivers to SUMMARY or AGENT.
        """
        self.visited_nodes.append("user_query_refinement")

        logger.debug(f"user_query_refinement: {state}")
        self.retrieved_documents = []
        history = convert_to_openai_messages(state.get("messages", []))
        latest_message = history[-1]["content"]
        previous_history = history[:-1]

        messages = [
            {
                "role": "system",
                "content": refinement_prompt(
                    messages=previous_history,
                    user_query=latest_message,
                ),
            }
        ]

        try:
            response = self.ollama_connector.chat(messages=messages)
            response_json = parse_json_markdown(response)
        except Exception:
            response_json = self.handle_unstructured_response()
        logger.debug(f"user_query_refinement: {response_json}")

        return {
            "action": response_json.get("action", "AGENT"),
            "refined_query": response_json.get("refined_query", ""),
            "plan": [],
            "completed_tasks": [],
            "current_task": None,
            "retrieved_documents": [],
            "steps": 0,
            "answer": None
        }

    @measure
    def create_plan(self, refined_query: str):
        messages = [
            {
                "role": "system",
                "content": agent_prompt(refined_query=refined_query),
            }
        ]

        try:
            response = self.ollama_connector.chat(messages=messages)
            plan = parse_json_markdown(response)

            if not isinstance(plan, list):
                logger.warning("Planner response is not a list.")
                return []
            return plan

        except Exception as e:
            logger.warning(f"Could not create plan: {e}")
            return []


    @measure
    def review_completed_work(self, state: SystemState):
        messages = [
            {
                "role": "system",
                "content": review_prompt(
                    refined_query=state["refined_query"],
                    completed_tasks=state.get("completed_tasks", []),
                ),
            }
        ]

        try:
            response = self.ollama_connector.chat(messages=messages)
            result = parse_json_markdown(response)
            return result

        except Exception as e:
            logger.warning(f"Could not review completed work: {e}")
            return {"action": "ANSWER", "new_tasks": []}

    @measure
    def agent(self, state: SystemState):
        """
        The brain of the system. It understands and decomposes the task into subtasks.
        """
        self.visited_nodes.append("agent")
        logger.debug(f"agent state: {state}")

        if state.get("steps", 0) >= MAX_NUM_OF_AGENT_STEPS:
            return {"action": "ANSWER"}

        plan = state.get("plan", [])
        unfinished = self.get_unfinished_tasks(state)
        if not plan:
            new_plan = self.create_plan(refined_query=state["refined_query"])
            return {
                "plan": new_plan,
                "action": "EXECUTE" if new_plan else "ANSWER",
                "steps": state.get("steps", 0) + 1
            }

        if unfinished:
            return {
                "action": "EXECUTE",
                "steps": state.get("steps", 0) + 1
            }

        review = self.review_completed_work(state)
        action = review.get("action", "ANSWER")
        new_tasks = review.get("new_tasks", [])

        if action == "EXECUTE" and new_tasks:
            return {
                "plan": plan + new_tasks,
                "action": "EXECUTE",
                "steps": state.get("steps", 0) + 1
            }

        return {
            "action": "ANSWER",
            "steps": state.get("steps", 0) + 1
        }

    @measure
    def select_next_task(self, state: SystemState):
        """
        Based on the subtask list it selects the next sub task.
        """
        self.visited_nodes.append("select_next_task")
        unfinished = self.get_unfinished_tasks(state)
        if not unfinished:
            return {"current_task": None}
        return {"current_task": unfinished[0]}
    
    @measure
    def route_agent(self, state: SystemState):
        """
        Simple routing function based on the state after agent.
        """
        if state.get("action") == "ANSWER":
            return "summarize"
        return "select_next_task"

    @measure
    def route_query(self, state: SystemState):
        """
        Simple routing function based on the state after user query refinement.
        """
        if state.get("action") == "SIMPLE":
            return "summarize"
        return "agent"
    
    @measure
    def route_task(self, state: SystemState):
        """
        Simple routing function based on the state after task.
        """
        current_task = state.get("current_task")
        if current_task is None:
            return "agent"
        task_type = current_task["type"]
        if task_type == "RAG":
            return "rag"
        if task_type == "TOOL":
            return "tool"
        return "summarize"

    @measure
    def summarize(self, state: SystemState):
        """
        The summarization module of the system which delivers the final answer to the user.
        """
        self.visited_nodes.append("summarize")
        logger.debug(f"summarize: {state}")
        messages = [
            {
                "role": "system",
                "content": summary_prompt(
                    refined_query=state["refined_query"],
                    completed_tasks=state.get("completed_tasks", []),
                ),
            }
        ]
        response = self.ollama_connector.chat(messages=messages)
        logger.debug(f"summarize: {response}")
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

    @measure
    def retrieve(self, state: SystemState):
        """
        Retrieval function based on the user/refined query or task.
        """
        self.visited_nodes.append("retrieve")
        current_task = (state["current_task"]["task"] or state["refined_query"])
        query_vector = self.sentence_embedder.embed(current_task)
        top_k_answers = self.vector_db.retrieve_top_k(query_vector=query_vector)
        return {"retrieved_documents": top_k_answers}
    
    @measure
    def rerank(self, state: SystemState):
        """
        Reranking function. It just copies the documents currently.
        """
        self.visited_nodes.append("rerank")
        reranked_documents = state.get("retrieved_documents", [])
        self.retrieved_documents += (reranked_documents)
        completed_tasks = state.get("completed_tasks", []).copy()
        completed_tasks.append(
            {
                "task_id": state["current_task"]["task_id"],
                "task": state["current_task"]["task"],
                "type": "RAG",
                "result": reranked_documents
            }
        )
        return {"completed_tasks": completed_tasks}

    @measure
    def tool(self, state: SystemState):
        """
        Tool usage module. Based on the state it calls the requested tools.
        """
        self.visited_nodes.append("tool")
        current_task = state["current_task"]
        tool, tool_args = current_task.get("tool", ""), current_task.get("tool_args", "")
        if tool == "stock_price":
            tool_result = get_stock_price(ticker=tool_args.get("ticker",""))
        elif tool == "financial_metric":
            tool_result = get_latest_financial_metric(ticker=tool_args.get("ticker",""), metric=tool_args.get("metric",""))
        else:
            raise ValueError(f"Unknown tool: {tool}")
        completed_tasks = state.get("completed_tasks", []).copy()
        completed_tasks.append({
            "task_id": current_task["task_id"],
            "task": current_task["task"],
            "type": "TOOL",
            "tool": tool,
            "result": tool_result,
        })
        return {"completed_tasks": completed_tasks}

    @measure
    def delete_chat(self, thread_id: str):
        """
        Backend part of the delete chat button.
        """
        self.checkpointer.delete_thread(thread_id)

    @measure
    def handle_unstructured_response(self):
        """
        Very basic route if we have a malformed answer.
        """
        return {"action": "ANSWER"}

    @measure
    def get_unfinished_tasks(self, state: SystemState):
        """
        Simple function which returns the unfinished subtasks from the task list.
        """
        plan = state.get("plan", [])
        completed_tasks = state.get("completed_tasks", [])
        completed_ids = [task["task_id"] for task in completed_tasks if task.get("task_id") is not None]
        unfinished = [task for task in plan if task["task_id"] not in completed_ids]
        return unfinished

if __name__ == "__main__":
    state = {
        "messages": [
                        {
                            "role": "user",
                            "content": "What medicine could i use for my leg if it hurts, can you check it on wikipedia?",
                        }
                    ]
    }
    config = {
        "configurable": {
            "thread_id": "test"
        }
    }
    backend_state_machine = BackendStateMachine()
    result = backend_state_machine.graph.invoke(state, config=config)

    print(result)