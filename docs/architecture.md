# Architecture Overview

This document describes the architecture, interfaces, and extension points of the Multi-AI Agentic Platform.


## High-Level Architecture
- **Core:** IDs, types, errors, and validation
- **Audit:** In-memory audit log, immutable audit events, event helpers
- **Tools:** Tool registry, tool protocol, fake tool client (for tests), **ModelRouter for model selection per node/task**
- **Workflow:** Workflow definition parser, engine, state management
- **Agents:** Agent registry, agent base classes
- **Adapters:** All external integrations (MCP, LangGraph, n8n, DB, SaaS) are adapters implementing platform interfaces

## Key Interfaces (Ports)
- `ToolClient`: `call(tool_name, args) -> result`
- `ArtifactStore`: `put(job_id, artifact)`, `get(ref)`
- `AuditLog`: `emit(event)`, `get_events(job_id)`
- `AgentRegistry`: `register(agent)`, `list()`, `get(name, version)`
- `WorkflowEngine`: `run(definition, input_artifact)`


- **Model Selection:** Use ModelRouter to select and route tool calls to specific GPT/model per node/task
- **Policy Enforcement:** Add tool/model allowlist (ToolAllowlistPolicy) and PII redaction (PiiRedactor) as middleware or node logic
- **Adapters:** Add new adapters for MCP, LangGraph, n8n, S3, DB, SaaS, etc. by implementing the relevant interface. Integration tests validate adapter contracts (see integration test for workflow engine with stubbed adapter). Real adapters (e.g., MCP) can return simulated or real responses.
- **Nodes:** Add new node types to the workflow engine (e.g., human review, branching, custom tools)
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
