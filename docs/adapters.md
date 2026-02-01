# Adapter Integrations

This document describes the adapter pattern and current integrations for the Agentic Platform.

## Adapter Pattern
- All external systems (MCP, LangGraph, n8n, S3, DB, SaaS) are integrated via adapters in `src/agentic_platform/adapters/`.
- Adapters expose a common interface: `call(tool_name, args)`.
- Adapters can be swapped for tests, simulation, or real backends.

## MCP Adapter
- File: `src/agentic_platform/adapters/mcp_adapter.py`
- Simulates a real MCP API call; ready for real HTTP/gRPC integration.
- Used in CLI, API, and tests.

## LangGraph (LangChain) Adapter
- File: `src/agentic_platform/adapters/langgraph_adapter.py`
- Supports both simulated and real HTTP POST calls to a LangGraph endpoint.
- Configure with `{ "endpoint": "http://your-langgraph-endpoint" }` to enable real calls.
- Used in CLI, API, and tests.

## Testing
- See `tests/unit/adapters/test_mcp_adapter.py` and `tests/unit/adapters/test_langgraph_adapter.py` for adapter tests.
- All adapters are covered by unit tests for both simulated and real (mocked) calls.
