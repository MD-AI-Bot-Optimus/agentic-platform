# ADR-003: Adapter Pattern for External Integrations

## Status
Accepted

## Context
The platform must support integration with multiple external systems (MCP, LangGraph, n8n, DB, SaaS) while keeping the core logic stable, testable, and decoupled from third-party dependencies.

## Decision
We use the Adapter Pattern for all external integrations. Each integration (e.g., MCP, LangGraph) is implemented as an adapter module in `src/agentic_platform/adapters/`. Adapters expose a common interface (e.g., `call(tool_name, args)`) and are swappable in tests and production.

**Relevant code:**
- Adapter modules: [src/agentic_platform/adapters/](../../src/agentic_platform/adapters/)
- Adapter interface example: [src/agentic_platform/adapters/mcp_adapter.py](../../src/agentic_platform/adapters/mcp_adapter.py)

## Consequences
- Core logic remains stable and testable.
- New integrations can be added without modifying core modules.
- Adapters can be stubbed for TDD and replaced with real implementations incrementally.
- All adapters must raise `NotImplementedError` until implemented.

## Related Milestones
- MCP adapter stub (2026-01-31)
- LangGraph adapter stub (2026-01-31)
