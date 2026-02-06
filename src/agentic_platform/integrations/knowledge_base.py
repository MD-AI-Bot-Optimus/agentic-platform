import time
from typing import Dict, Any
from .base import KnowledgeBaseProvider

class MockKnowledgeBase(KnowledgeBaseProvider):
    """
    In-memory simulated knowledge base for development and testing.
    Fast, deterministic, and requires no external dependencies.
    """
    def search(self, query: str) -> str:
        query = query.lower()
        if "neural network" in query:
            return "Found 5 articles: 'Neural Networks 101', 'Deep Learning Basics', 'Backpropagation Explained'. Summary: Neural networks are computing systems inspired by biological brains..."
        elif "transformer" in query:
            return "Found 3 articles: 'Attention Is All You Need', 'BERT Architecture', 'GPT Models'. Summary: Transformers use self-attention to process sequential data in parallel..."
        elif "langgraph" in query:
            return "Found documentation: LangGraph is a library for building stateful, multi-agent applications with LLMs..."
        else:
            return f"Found 2 general articles about '{query}'. They discuss basic concepts and history."

class EnterpriseKnowledgeBase(KnowledgeBaseProvider):
    """
    Simulated Enterprise Vector Store integration.
    Mimics the behavior of a production-grade system (e.g., Pinecone, Weaviate, Elasticsearch)
    including connection latency, structured metadata, and access control checks.
    """
    def __init__(self, connection_string: str = "mock://enterprise-vector-db"):
        self.connection_string = connection_string
        # Simulate connection pool initialization
        print(f"[EnterpriseKB] Initializing connection pool to {connection_string}...")
        
    def search(self, query: str) -> str:
        # Simulate network latency (e.g., 200ms)
        time.sleep(0.2)
        
        # Simulate a structured enterprise response
        return (
            f"--- ENTERPRISE SEARCH RESULT ---\n"
            f"Source: Corporate Knowledge Vector Store (Shard US-East-1)\n"
            f"Query Latency: 215ms\n"
            f"Access Control: Verified (User: agent-service-account)\n"
            f"--------------------------------\n"
            f"Top Matches for '{query}':\n\n"
            f"1. [DOC-8821] Internal Architecture Guide v2.pdf (Score: 0.92)\n"
            f"   > ...regarding '{query}', the system employs a distributed consistency model...\n\n"
            f"2. [WIKI-192] Engineering Onboarding (Score: 0.88)\n"
            f"   > ...best practices for implementing '{query}' in our stack include using the shared library...\n\n"
            f"3. [JIRA-4420] Deprecation Notice (Score: 0.75)\n"
            f"   > ...legacy support for '{query}' will be removed in Q4..."
        )
