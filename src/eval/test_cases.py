TEST_CASES = [
    {
        "query": "Tell me about NVIDIA",
        "expected_types": ["RAG"],
    },
    {
        "query": "What is NVIDIA's current stock price?",
        "expected_types": ["TOOL"],
    },
    {
        "query": "What is Apple's latest revenue?",
        "expected_types": ["TOOL"],
    },
    {
        "query": "Compare NVIDIA and Apple companies",
        "expected_types": ["RAG", "RAG"],
    },
    {
        "query": "Compare Amazon and NVIDIA",
        "expected_types": ["RAG", "RAG"],
    },
    {
        "query": "Tell me about Microsoft's business and its current stock price",
        "expected_types": ["RAG", "TOOL"],
    },
    {
        "query": "Compare Apple and NVIDIA and give me their current stock prices",
        "expected_types": ["RAG", "RAG", "TOOL", "TOOL"],
    },
    {
        "query": "What are Amazon's main business areas and latest EPS?",
        "expected_types": ["RAG", "TOOL"],
    },
]