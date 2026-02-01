

# Multi-AI Agentic Platform (MVP)

## Overview
This project is a modular, test-driven platform for orchestrating multi-agent workflows, designed for easy integration with external systems (MCP, LangGraph, n8n, DB, SaaS) via adapters. All core logic is decoupled from integrations and fully tested.

## Current Status ✅
- **Phase 7 Complete:** MCP Server Integration with 57 passing tests
- **Core Features:** Workflow engine, audit trails, OCR integration, MCP protocol support
- **Modern UI:** React with Material-UI, 2-column responsive layout, Highway 1 background
- **API:** FastAPI with OCR, workflow execution, and MCP endpoints
- **Documentation:** Complete ADRs, MCP guide, API docs, testing strategy

## Quick Links
- [Roadmap & TDD Commit History](docs/roadmap.md)
- [MCP Implementation Guide](docs/mcp-guide.md)
- [API Documentation](docs/api.md)
- [Integration Plan: MCP, LangGraph, n8n](docs/integrations.md)
- [Architecture Overview](docs/architecture.md)
- [Testing Strategy](docs/testing.md)
- [Cloud Run Deployment](docs/CLOUD_RUN_DEPLOYMENT.md)
- [Architectural Decision Records (ADRs)](docs/decisions/)

## Features
✅ **Workflow Engine** - YAML-based workflow definitions with conditional branching  
✅ **Audit Trail** - Immutable audit logs with full correlation tracking  
✅ **OCR Integration** - Google Cloud Vision API with formatted output  
✅ **MCP Protocol** - JSON-RPC 2.0 server and client implementation  
✅ **Tool Registry** - Pluggable tool system with discovery  
✅ **Model Selection** - Route tool calls to specific models per task  
✅ **Policy Enforcement** - Tool and model allowlist policies  
✅ **PII Redaction** - Middleware for sensitive data redaction  
✅ **Modern React UI** - Responsive dashboard with Material-UI  
✅ **FastAPI Backend** - Production-ready REST API  

## Quickstart (Modern UI & API)

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Cloud SDK (for OCR)

### 1. Clone and Start Everything

```sh
git clone <repo-url>
cd agentic-platform
chmod +x start_all.sh
./start_all.sh
```

This will start:
- **Backend API** (FastAPI) on http://localhost:8002
- **Frontend UI** (React/Material-UI) on http://localhost:5173

### 2. Using the Modern UI

Open **http://localhost:5173** in your browser to access:
- **OCR Demo** - Upload images for text extraction
- **MCP Tool Tester** - Test any registered MCP tool with JSON arguments
- **Workflow Runner** - Execute custom YAML workflows
- **Results Dashboard** - View workflow results, tool outputs, and audit logs

**UI Features:**
- 2-column responsive grid layout
- Highway 1 Pacific Coast background imagery
- Sticky header for easy navigation
- Real-time workflow execution with JSON response display

### 3. Using the CLI

```sh
python -m src.agentic_platform.cli demo_workflow.yaml demo_input.json
```

### 4. Using the API

Start the API server:
```sh
PYTHONPATH=src uvicorn src.agentic_platform.api:app --reload --port 8002
```

**OCR Example:**
```sh
curl -X POST http://localhost:8002/run-ocr/ \
  -F "image=@sample_data/letter.jpg"
```

**Workflow Example:**
```sh
curl -F "workflow=@demo_workflow.yaml" \
     -F "input_artifact=@demo_input.json" \
     http://localhost:8002/run-workflow/
```

**MCP Tools Discovery:**
```sh
curl http://localhost:8002/mcp/tools | jq
```

**MCP Tool Call:**
```sh
curl -X POST http://localhost:8002/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "sample_data/letter.jpg"}
    },
    "id": 1
  }'
```

See [docs/api.md](docs/api.md) for detailed API documentation.

### 5. Running Tests

```sh
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration

# Specific test file
pytest tests/unit/adapters/test_mcp_server.py
```

---

## Repository Structure

```
agentic-platform/
├── README.md
├── pyproject.toml
├── pytest.ini
├── start_all.sh
├── docs/
│   ├── roadmap.md              # TDD milestone history
│   ├── mcp-guide.md            # MCP implementation details
│   ├── api.md                  # API reference
│   ├── architecture.md         # System design
│   ├── adapters.md             # Adapter system
│   ├── integrations.md         # Integration plan
│   ├── testing.md              # Testing strategy
│   └── decisions/              # ADRs (Architecture Decision Records)
├── src/
│   └── agentic_platform/
│       ├── __init__.py
│       ├── api.py              # FastAPI application
│       ├── cli.py              # CLI runner
│       ├── core/               # Core types and utilities
│       ├── agents/             # Agent implementations
│       ├── audit/              # Audit trail system
│       ├── tools/              # Tool registry and middleware
│       ├── workflow/           # Workflow engine
│       └── adapters/           # MCP, LangGraph, etc.
├── tests/
│   ├── unit/                   # Unit tests
│   │   ├── adapters/
│   │   ├── agents/
│   │   ├── audit/
│   │   ├── core/
│   │   ├── tools/
│   │   └── workflow/
│   └── integration/            # Integration tests
├── ui/
│   ├── README.md
│   ├── package.json
│   ├── vite.config.js
│   ├── public/                 # Static assets
│   │   └── magicalmajestichighway1.jpg
│   └── src/
│       ├── App.jsx             # Main React app
│       ├── index.html
│       └── main.jsx
└── sample_data/                # Test images
    ├── letter.jpg
    ├── handwriting.jpg
    ├── numbers_gs150.jpg
    └── stock_gs200.jpg
```

---

## Development Workflow

### Adding a New Tool

1. Implement tool in `src/agentic_platform/tools/`
2. Register in `ToolRegistry`
3. Add unit tests in `tests/unit/tools/`
4. MCP endpoint will auto-discover it via `/mcp/tools`

### Creating a Workflow

1. Define YAML with nodes and edges:
   ```yaml
   nodes:
     - id: ocr_step
       tool: google_vision_ocr
       params: { image_path: "image.jpg" }
   edges:
     - from: ocr_step
       to: process_step
   ```

2. Submit via UI, CLI, or API

### Integration with External Systems

All integrations use the adapter pattern:
- `MCPAdapter` - JSON-RPC 2.0 protocol for tool discovery
- `LangGraphAdapter` - Graph-based workflow orchestration  
- More adapters coming (n8n, custom systems)

---

## Testing

- **Unit Tests:** 50+ tests for core logic, adapters, agents
- **Integration Tests:** 13+ tests for end-to-end workflows and OCR
- **MCP Tests:** 22 MCPServer + 22 MCPAdapter + 13 E2E = 57 total
- **Coverage:** Core logic has >90% coverage

Run tests:
```sh
pytest
pytest --cov=src/agentic_platform
```

---

## Documentation

All documentation is in `docs/`:
- **Roadmap** - Phase-by-phase development history (TDD)
- **MCP Guide** - Detailed MCP server and protocol implementation
- **API Docs** - Full REST API reference with examples
- **Architecture** - System design, patterns, and principles
- **ADRs** - Architectural decision records for major choices
- **Testing** - Test strategy, fixtures, and patterns

---

## Next Steps

1. **Phase 8 - LangGraph Integration** - Graph-based workflow orchestration
2. **Phase 9 - n8n Integration** - Visual workflow builder
3. **Phase 10 - Database Artifact Store** - Persistent storage layer
4. **Phase 11 - Advanced Policies** - Role-based access control, rate limiting

---

## Support & Contributing

For issues, questions, or contributions, please refer to the documentation in `docs/` and the inline code comments. The codebase follows TDD principles and is fully documented.