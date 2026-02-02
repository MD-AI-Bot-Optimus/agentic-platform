# 🤖 Agentic Platform

A production-ready, test-driven platform for building multi-agent workflows with full Model Context Protocol (MCP) support, tool orchestration, and audit trails.

**🌐 Live Demo:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/

## ✨ Current Status

- ✅ **Phase 7:** MCP Server Integration with 57 passing tests
- ✅ **Production:** Deployed to Google Cloud Run with auto-scaling
- ✅ **Modern UI:** Live React dashboard with Material-UI
- ✅ **Complete:** Full documentation, API reference, ADRs

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [**MCP.md**](docs/MCP.md) | Model Context Protocol implementation & integration guide |
| [**API.md**](docs/api.md) | REST API reference for all endpoints |
| [**Architecture.md**](docs/architecture.md) | System design and component overview |
| [**Adapters.md**](docs/adapters.md) | Tool registry and adapter patterns |
| [**Testing.md**](docs/testing.md) | Testing strategy and test coverage |
| [**Roadmap.md**](docs/roadmap.md) | TDD milestone history and project roadmap |
| [**Decisions**](docs/decisions/) | Architecture Decision Records (ADRs 1-10) |

## 🚀 Quick Start

### Try Live Demo
Visit: **https://agentic-platform-api-7erqohmwxa-uc.a.run.app/**

- Use OCR demo to extract text from images
- Test MCP tools with JSON arguments
- Run workflows and see results

### Local Development

```bash
# Clone
git clone <repo-url>
cd agentic-platform

# Start everything (requires Python 3.12+, Node.js 18+)
chmod +x start_all.sh
./start_all.sh

# Access:
# - UI: http://localhost:5173
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Docker

```bash
docker build -t agentic-platform .
docker run -p 8080:8080 agentic-platform
# Visit http://localhost:8080
```

## 🛠️ API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Welcome page |
| GET | `/docs` | Interactive API docs |
| GET | `/mcp/tools` | List all MCP tools |
| POST | `/mcp/request` | Call a tool (JSON-RPC 2.0) |
| POST | `/run-ocr/` | Extract text from image |
| POST | `/run-workflow/` | Execute workflow |

### Example: OCR

```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/run-ocr/ \
  -F "image=@document.jpg"
```

### Example: MCP Tool Call

```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "image.jpg"}
    },
    "id": 1
  }'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   UI (React + Material-UI)          │
│   - OCR Demo                        │
│   - MCP Tool Tester                 │
│   - Workflow Runner                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  FastAPI Backend                    │
│  - REST Endpoints                   │
│  - MCP Server (JSON-RPC 2.0)        │
│  - OCR Workflow Integration         │
└──────────────┬──────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌───────────────┐ ┌──────────────┐
│ Workflow      │ │ Tool         │
│ Engine        │ │ Registry     │
└───────────────┘ └──────────────┘
      │                  │
      ▼                  ▼
┌──────────────────────────────────────┐
│ Adapters & Tools                     │
│ - MCP Adapter                        │
│ - Google Vision OCR                  │
│ - Policy Middleware                  │
│ - Audit Trail                        │
└──────────────────────────────────────┘
```

## 📦 Structure

```
agentic-platform/
├── src/agentic_platform/
│   ├── api.py           # FastAPI app
│   ├── workflow/        # Workflow engine
│   ├── tools/           # Tool registry & policies
│   ├── adapters/        # MCP, LangGraph, integrations
│   ├── audit/           # Audit logging
│   └── agents/          # Agent implementations
├── ui/                  # React frontend
├── tests/               # 57+ tests (unit + integration)
├── docs/                # Complete documentation
└── deploy/              # Cloud Run configuration
```

## ✅ Features

- **Workflow Engine** - YAML-based workflows with branching
- **MCP Protocol** - Full JSON-RPC 2.0 compliance
- **OCR** - Google Vision API integration
- **Tool Registry** - Pluggable tool discovery system
- **Audit Trails** - Immutable event logging
- **Policy Enforcement** - Tool & model allowlists
- **Modern UI** - Responsive React dashboard
- **Production Ready** - Docker, Cloud Run, auto-scaling
- **57+ Tests** - Comprehensive test coverage
- **Full Documentation** - API, architecture, decisions

## 🧪 Testing

```bash
# All tests
pytest -v

# With coverage
pytest --cov=src tests/

# Watch mode
pytest-watch
```

**Status:** 57 tests passing ✅

## 🔧 Technologies

- **Backend:** Python 3.12, FastAPI, Pydantic v2
- **Frontend:** React 18, Material-UI 5, Vite
- **Cloud:** Google Cloud Run, Cloud Build
- **Standards:** JSON-RPC 2.0, OpenAPI 3.0, MCP 1.0
- **Testing:** pytest, pytest-cov

## 🚢 Deployment

Automatic deployment to Google Cloud Run on every GitHub push.

**Current Deployment:**
- URL: https://agentic-platform-api-7erqohmwxa-uc.a.run.app/
- Region: us-central1
- Memory: 512Mi
- Status: ✅ Live

See [Deployment Guide](docs/DEPLOYMENT.md) for details.

## 🔐 Security

- Immutable audit trails for compliance
- PII redaction middleware
- CORS protection
- Input validation
- Token-based auth (extensible)

## 📈 Roadmap

| Phase | Status | Goals |
|-------|--------|-------|
| 7 | ✅ Done | MCP Server, Tool Registry |
| 8 | 🔄 In Progress | UI improvements, perf tuning |
| 9 | 📋 Planned | LangGraph adapter |
| 10 | 📋 Planned | n8n integration |
| 11 | 📋 Planned | Database artifact storage |

See [Roadmap.md](docs/roadmap.md) for full TDD history.

## 🤝 Integration Examples

### Python
```python
import requests

response = requests.post(
    'https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request',
    json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'google_vision_ocr',
            'arguments': {'image_path': 'doc.jpg'}
        },
        'id': 1
    }
)
print(response.json())
```

### Node.js
```javascript
const response = await fetch(
  'https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'google_vision_ocr',
        arguments: { image_path: 'doc.jpg' }
      },
      id: 1
    })
  }
);
```

### Claude (Future)
```bash
claude --mcp https://agentic-platform-api-7erqohmwxa-uc.a.run.app
```

## 📄 License

MIT

---

**Built with ❤️ for AI-powered automation** | [Live Demo](https://agentic-platform-api-7erqohmwxa-uc.a.run.app/) | [Docs](docs/)
