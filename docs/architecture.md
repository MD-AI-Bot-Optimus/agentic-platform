# Architecture Overview

This document describes the architecture, interfaces, and extension points of the Multi-AI Agentic Platform.

## High-Level Architecture
- **Core:** IDs, types, errors, and validation
- **Audit:** In-memory audit log, immutable audit events, event helpers
- **Tools:** Tool registry, tool protocol, fake tool client (for tests)
- **Workflow:** Workflow definition parser, (future) engine, state management
- **Agents:** (Planned) agent registry, agent base classes
- **Adapters:** All external integrations (MCP, LangGraph, n8n, DB, SaaS) are adapters implementing platform interfaces

## Key Interfaces (Ports)
- `ToolClient`: `call(tool_name, args) -> result`
- `ArtifactStore`: `put(job_id, artifact)`, `get(ref)`
- `AuditLog`: `emit(event)`, `get_events(job_id)`
- `AgentRegistry`: `register(agent)`, `list()`, `get(name, version)`
- `WorkflowEngine`: `run(definition, input_artifact)`

## Extension Points
- **Adapters:** Add new adapters for MCP, LangGraph, n8n, S3, DB, etc. by implementing the relevant interface
- **Nodes:** Add new node types to the workflow engine (e.g., human review, branching, custom tools)
- **Policies:** Add policy enforcement (e.g., tool allowlist, PII redaction) as middleware or node logic
- **Observability:** Plug in real audit/trace, metrics, and logging backends

## Design Principles
- **Separation of Concerns:** Core logic is isolated from integrations
- **Testability:** All interfaces are mockable; high test coverage is enforced
- **Configurable:** Use dependency injection or config files to select implementations
- **Milestone-Driven:** All major changes are committed as vertical slices with passing tests

## ADRs
See `docs/decisions/` for Architectural Decision Records documenting key design choices and tradeoffs.

---

This architecture enables rapid iteration, safe refactoring, and easy integration of new technologies as the platform evolves.
