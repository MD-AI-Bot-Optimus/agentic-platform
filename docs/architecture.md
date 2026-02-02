## CLI Interface
The platform provides a minimal CLI (`src/agentic_platform/cli.py`) for running workflows from YAML definitions and JSON input artifacts. This enables end-to-end testing and usage without code changes, and provides a foundation for future API or UI integration.


# Architecture Overview (with Modern UI)

See [docs/adapters.md](adapters.md) for details on the adapter pattern and current integrations.


This document describes the architecture, interfaces, and extension points of the Multi-AI Agentic Platform, including the new React/Material UI frontend for workflow orchestration and debugging.


## High-Level Architecture
- **UI:** Modern React frontend (Material-UI with 2-column grid layout, Highway 1 background)
  - OCR demo for image text extraction
  - MCP tool tester for tool discovery and execution
  - Workflow runner for YAML execution
  - Results dashboard with audit log visualization
- **API:** FastAPI backend with multiple endpoints:
  - `/run-ocr/` - Image processing with Google Vision API
  - `/run-workflow/` - Workflow execution with adapter selection
  - `/mcp/tools` - MCP tool discovery
  - `/mcp/request` - MCP JSON-RPC 2.0 protocol handler
- **Core:** IDs, types, errors, and validation
- **Audit:** In-memory audit log, immutable audit events with correlation tracking
- **Tools:** 
  - Tool registry with plugin system
  - Tool protocol for standardized interfaces
  - ModelRouter for model selection per node/task
  - GoogleVisionOCR for OCR via Google Cloud Vision API
  - Policies: ToolAllowlistPolicy, PiiRedactor middleware
- **Workflow:** 
  - YAML-based workflow definitions (nodes + edges)
  - Engine with conditional branching and retry logic
  - State management and artifact linking
- **Agents:** Agent registry, base classes, artifact store integration
- **Adapters:** All external integrations implement adapter pattern:
  - **MCPAdapter** - JSON-RPC 2.0 protocol for tool discovery and calling ✅ IMPLEMENTED
  - **LangGraphAdapter** - Stub only, returns simulated responses (not yet implemented)
  - **n8nAdapter** - Not yet implemented
  - **S3ArtifactStore**, **DBArtifactStore** - Artifact persistence (not yet implemented)
  - **GoogleVisionOCR** - Image text extraction ✅ IMPLEMENTED
- **Integrations:** Google Cloud SDK (Application Default Credentials for auth)

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
