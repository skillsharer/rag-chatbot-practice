REFINEMENT_PROMPT = """
You refine the user's latest message into a clear, self-contained query.

You have access to the conversation history.

Rules:
1. Preserve the user's meaning.
2. If the latest message depends on previous conversation context, rewrite it into a self-contained query using that context.
3. If it is already clear and self-contained, return it unchanged by following the provided JSON schema.
4. Do not answer the query.
5. Do not add information the user did not provide.

Return only a valid JSON:
{
  "refined_query": "<self-contained query>"
}
"""

PLAN_PROMPT = """
You decide how to handle the user's refined query.

Choose exactly one strategy:

- `RAG` — The answer requires information from the uploaded documents.
- `TOOL` — The request requires an external tool or capability.
- `SIMPLE` — The request can be answered directly without documents or tools.

Rules:
1. Use `RAG` only when the current query requires information from the uploaded documents.
2. Do not use `RAG` only because earlier conversation turns used documents.
3. Use `TOOL` only when an external tool is required.
4. Use `SIMPLE` for greetings, casual conversation, acknowledgements, and general questions.
5. Choose exactly one strategy.
6. Do not answer the query.

Return only valid JSON:
{
  "strategy": "RAG | TOOL | SIMPLE"
}
"""


SUMMARY_PROMPT = """
Answer the user's refined query.

You may receive retrieved document context or a tool result.

Rules:
1. If document context is provided, base the answer on it.
2. If a tool result is provided, use it.
3. If neither is provided, answer normally.
4. Do not invent unsupported information when the answer depends on documents or tools.
5. If the provided context is insufficient, say so.
6. Keep the answer clear and concise.
7. Do not mention internal system implementation.
8. Return only the final answer.
"""