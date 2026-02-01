# ADR-003: Adapter Pattern for External Integrations

## Status
Accepted

## Context
The platform must support integration with multiple external systems (MCP, LangGraph, n8n, DB, SaaS) while keeping the core logic stable, testable, and decoupled from third-party dependencies.

## Decision
We use the Adapter Pattern for all external integrations. Each integration (e.g., MCP, LangGraph) is implemented as an adapter module in `src/agentic_platform/adapters/`. Adapters expose a common interface (e.g., `call(tool_name, args)`) and are swappable in tests and production.

**Relevant code:**
- All adapters are implemented in [src/agentic_platform/adapters/](../../src/agentic_platform/adapters/). Each adapter (e.g., MCP, LangGraph, n8n, S3, DB, SaaS) is a separate module following a common interface.
- The adapter interface (see [src/agentic_platform/adapters/mcp_adapter.py](../../src/agentic_platform/adapters/mcp_adapter.py)) defines the contract for tool calls and artifact storage. Adapters can be swapped in the workflow engine and are used in both unit and integration tests.

## Consequences
- Core logic remains stable and testable.
- New integrations can be added without modifying core modules.
- Adapters can be stubbed for TDD and replaced with real implementations incrementally.
- All adapters must raise `NotImplementedError` until implemented.

## Related Milestones
- MCP adapter stub (2026-01-31)
- LangGraph adapter stub (2026-01-31)
