## CLI Interface
The platform provides a minimal CLI (`src/agentic_platform/cli.py`) for running workflows from YAML definitions and JSON input artifacts. This enables end-to-end testing and usage without code changes, and provides a foundation for future API or UI integration.


# Architecture Overview (with Modern UI)

See [docs/adapters.md](adapters.md) for details on the adapter pattern and current integrations.


This document describes the architecture, interfaces, and extension points of the Multi-AI Agentic Platform, including the new React/Material UI frontend for workflow orchestration and debugging.


## High-Level Architecture
- **UI:** Modern React frontend (Material UI) for workflow execution, OCR, adapter selection, and result/audit log visualization
- **API:** FastAPI backend with `/run-ocr/` and `/run-workflow/` endpoints
- **Core:** IDs, types, errors, and validation
- **Audit:** In-memory audit log, immutable audit events, event helpers
- **Tools:** Tool registry, tool protocol, fake tool client (for tests), **ModelRouter for model selection per node/task**, **GoogleVisionOCR for OCR**
- **Workflow:** Workflow definition parser (YAML with nodes/edges), engine, state management
- **Agents:** Agent registry, agent base classes
- **Adapters:** All external integrations (MCP, LangGraph, n8n, DB, SaaS, Google Vision) are adapters implementing platform interfaces. See [adapters.md](adapters.md).
- **Google Cloud Integration:** Application Default Credentials (ADC) for authentication, Cloud Vision API for OCR

## Key Interfaces (Ports)
- `ToolClient`: `call(tool_name, args) -> result`
- `ArtifactStore`: `put(job_id, artifact)`, `get(ref)`
- `AuditLog`: `emit(event)`, `get_events(job_id)`
- `AgentRegistry`: `register(agent)`, `list()`, `get(name, version)`
- `WorkflowEngine`: `run(definition, input_artifact)`


- **Model Selection:** Use ModelRouter to select and route tool calls to specific GPT/model per node/task
- **OCR Integration:** GoogleVisionOCR adapter uses Google Cloud Vision API via Application Default Credentials (ADC); separate `/run-ocr/` endpoint for image processing
- **Policy Enforcement:** Add tool/model allowlist (ToolAllowlistPolicy) and PII redaction (PiiRedactor) as middleware or node logic
- **Error Handling & Observability:** The workflow engine emits STEP_STARTED before tool calls and STEP_ERRORED if a tool call fails, ensuring robust audit logging and traceability for all workflow runs.
- **Adapters:** Add new adapters for MCP, LangGraph, n8n, S3, DB, SaaS, Google Vision, etc. by implementing the relevant interface. Integration tests validate adapter contracts. Real adapters can return simulated or real responses.
- **Nodes:** Add new node types to the workflow engine (e.g., human review, branching, custom tools, OCR)
- **Observability:** Plug in real audit/trace, metrics, and logging backends

## Design Principles
- **User Experience:** Modern, responsive UI for easy workflow execution and debugging
- **Separation of Concerns:** Core logic is isolated from integrations
- **Testability:** All interfaces are mockable; high test coverage is enforced
- **Configurable:** Use dependency injection or config files to select implementations
- **Milestone-Driven:** All major changes are committed as vertical slices with passing tests

## ADRs
See `docs/decisions/` for Architectural Decision Records documenting key design choices and tradeoffs.

---

This architecture enables rapid iteration, safe refactoring, and easy integration of new technologies as the platform evolves.
