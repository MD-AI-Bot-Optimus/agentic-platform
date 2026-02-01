

# Multi-AI Agentic Platform (MVP)

## Overview
This project is a modular, test-driven platform for orchestrating multi-agent workflows, designed for easy integration with external systems (MCP, LangGraph, n8n, DB, SaaS) via adapters. All core logic is decoupled from integrations and fully tested.

## Quick Links
- [Roadmap & TDD Commit History](docs/roadmap.md)
- [Integration Plan: MCP, LangGraph, n8n](docs/integrations.md)
- [Architecture Overview](docs/architecture.md)
- [Testing Strategy](docs/testing.md)
- [Architectural Decision Records (ADRs)](docs/decisions/)

## Repo Structure
```
kre-agentic-platform/
  pyproject.toml
  README.md
  src/
    agentic_platform/
      ...
  tests/
    unit/
    integration/
  docs/
    roadmap.md
    integrations.md
    architecture.md
    testing.md
    decisions/
```


## Status
- Core logic, types, and interfaces implemented and fully tested
- Model selection per node/task supported and tested (route tool calls to specific GPT/model as specified in workflow)
- Policy enforcement (tool/model allowlist) supported and tested (ToolAllowlistPolicy)
- PII redaction middleware supported and tested (PiiRedactor)
- All external systems are mocked or abstracted behind interfaces
- Milestone-driven, TDD-first development
- Ready for incremental integration of MCP, LangGraph, n8n, and more

See the linked docs for detailed plans, architecture, and progress.
This project is built to be integration-ready. As the platform matures, MCP, LangGraph, and n8n will be incorporated as adapters, ensuring the core remains stable, testable, and easy to extend. All progress and integration steps will be milestone-driven and documented.



## Quickstart (Modern UI & API)

### 1. Clone and Start Everything

```sh
git clone <repo-url>
cd agentic-platform
chmod +x start_all.sh
./start_all.sh
```

This will start:
- Backend API (FastAPI) on http://localhost:8002
- Frontend UI (React/Material UI) on http://localhost:5173

### 2. Using the UI

Open http://localhost:5173 in your browser. Upload a workflow YAML and input JSON, select an adapter, and run workflows with a modern, responsive interface.

### 3. Using the CLI

```sh
python -m src.agentic_platform.cli demo_workflow.yaml demo_input.json
```

### 4. Using the API

Start the API server (if not using the script):
```sh
PYTHONPATH=src uvicorn src.agentic_platform.api:app --reload --port 8002
```
Run a workflow via API:
```sh
curl -F "workflow=@demo_workflow.yaml" -F "input_artifact=@demo_input.json" http://localhost:8002/run-workflow/
```
See docs/api.md for details.

### 5. Running Tests

```sh
pytest
```

---

## Modern UI

The React frontend now uses Material UI for a modern, responsive look. All workflow results, tool outputs, and audit logs are clearly displayed. See `ui/` for source and tests.

---