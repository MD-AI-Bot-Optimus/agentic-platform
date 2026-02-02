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
- **Status:** Stub only - returns simulated responses
- Currently does NOT have real LangGraph implementation
- No graph execution, state management, or LLM integration
- Dependencies missing: `langgraph`, `langchain`, LLM providers
- **Future:** Real implementation requires:
  - Install: `pip install langgraph langchain anthropic`
  - StateGraph definition with agent/tool/decision nodes
  - LLM integration (e.g., Claude, GPT-4)
  - Tool binding for MCP tools
  - Streaming support for real-time responses
- See `LANGGRAPH_ROADMAP.md` for implementation plan

## Adapter Selection (API & CLI)
- The API `/run-workflow/` endpoint accepts an `adapter` form field (`mcp` or `langgraph`).
- The CLI accepts `--adapter mcp` or `--adapter langgraph`.
- This allows runtime selection of the backend for tool calls.

## Testing
- See `tests/unit/adapters/test_mcp_adapter.py` and `tests/unit/adapters/test_langgraph_adapter.py` for adapter tests.
- All adapters are covered by unit tests for both simulated and real (mocked) calls.
