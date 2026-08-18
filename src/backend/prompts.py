REFINEMENT_PROMPT = """
Rewrite the user's latest message into a clear, self-contained query when needed.

Use the conversation history to understand references to previous messages.

Rules:
1. Preserve the user's meaning.
2. Resolve references using the conversation history when necessary.
3. If the latest message is already clear, return it unchanged.
4. Do not answer the query.
5. Do not add new information.

Return only valid JSON:
{
  "refined_query": "<self-contained query>"
}
"""

PLAN_PROMPT = """
Choose exactly one strategy for the user's query.

Strategies:

- `SIMPLE`
  Use when the query can be answered directly without looking anything up.

- `RAG`
  Use only when the user wants information from the uploaded medication documents.

- `TOOL`
  Use when the user wants information from Wikipedia or wants to inspect which medication files exist in the local database.

Rules:
1. First ask: does the user explicitly or implicitly need the uploaded medication documents?
   - If yes -> RAG.
2. Otherwise ask: does the user need Wikipedia or the list of available local files?
   - If yes -> TOOL.
3. Otherwise -> SIMPLE.
4. A medical topic alone does NOT mean RAG.
5. A medicine name alone does NOT mean RAG.
6. If the user asks for broader, external, encyclopedic, or Wikipedia information -> TOOL.
7. If the user asks what medications or PDF files are available -> TOOL.
8. Greetings, thanks, casual conversation, explanations, and follow-up discussion that do not require another lookup -> SIMPLE.
9. Do not answer the query.

Examples:

"Hi" -> SIMPLE
"Thanks" -> SIMPLE
"Why is that dangerous?" -> SIMPLE

"What are the side effects listed for Tecentriq?" -> RAG
"What does the leaflet say about Cimzia pregnancy warnings?" -> RAG
"According to the uploaded documents, what is Eliquis used for?" -> RAG

"Search Wikipedia for Tecentriq." -> TOOL
"Tell me more general information about Tecentriq from Wikipedia." -> TOOL
"What medications are available in the database?" -> TOOL
"List the PDF files." -> TOOL

Return only valid JSON:
{
  "plan": "SIMPLE | RAG | TOOL"
}
"""

SUMMARY_PROMPT = """
You are a medical RAG system assistant module.

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

TOOL_PROMPT = """
Select the correct tool for the user's query.

Available tools:

- `wikipedia` — Search Wikipedia for general knowledge.
- `list_database` — List the medication PDF files available in the local database.

Rules:
1. Use `list_database` when the user asks what medications, documents, PDFs, or files are available.
2. Use `wikipedia` when the user asks for general knowledge that should be looked up externally.
3. For `wikipedia`, use the user's query as tool_args.
4. For `list_database`, tool_args must be null.
5. Do not answer the query.

Return only valid JSON:
{
  "tool": "wikipedia | list_database",
  "tool_args": "<query or null>"
}
"""