# 🤖 Agentic Platform

A production-ready, test-driven foundation for building multi-agent AI workflows with **OCR**, **MCP protocol**, **tool orchestration**, and **audit trails**. 

**🌐 Live Demo:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/ | **✅ Status:** Phase 8 Complete | **🚀 Phase 9:** LangGraph (In Progress)

## ✨ Key Features

- **🏗️ Enterprise Architecture** - Modular design with adapter pattern and clean separation of concerns
- **🔌 MCP Server Integration** - Full Model Context Protocol support for tool orchestration
- **🧪 Test-Driven Development** - 57+ passing tests with comprehensive coverage
- **📊 Audit & Compliance** - Immutable audit logs for every action
- **☁️ Cloud-Ready** - Deployed to Google Cloud Run with auto-scaling
- **🎨 Modern UI** - React + Material-UI dashboard with OCR & workflow executor
- **🚀 Production Ready** - Fully operational OCR, workflow engine, and MCP server

## ✨ Production-Ready Features (Phase 8 ✅)

- **OCR Engine** - Google Vision API with intelligent confidence scoring
- **MCP Server** - Full JSON-RPC 2.0 compliance with tool registry
- **Workflow Engine** - YAML-based workflows with branching and retry policies
- **Audit Trail** - Immutable event logging with correlation IDs
- **Cloud Deployment** - Google Cloud Run with auto-scaling
- **Modern UI** - React 18 + Material-UI dashboard
- **57+ Tests** - Comprehensive unit & integration test coverage

## 🔄 In Development (Phase 9)

- **LLM Integration** - Claude, GPT-4, Gemini via LangGraph
- **Agent Memory** - Multi-step conversation context
- **RAG System** - Knowledge grounding and retrieval
- **Streaming UI** - Real-time token streaming and visualization

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) | 🚀 Deployment to Google Cloud Run |
| [**API.md**](docs/api.md) | 📖 Complete REST API reference |
| [**Architecture.md**](docs/architecture.md) | 🏗️ System design overview |
| [**CONTRIBUTING.md**](docs/CONTRIBUTING.md) | 💻 Development standards |
| [**MCP.md**](docs/MCP.md) | 🔌 MCP protocol implementation |
| [**Testing.md**](docs/testing.md) | 🧪 Test strategy & coverage |
| [**Decisions**](docs/decisions/) | 📋 Architecture Decision Records |

## 🚀 Quick Start

### Option 1: Live Demo
Visit **https://agentic-platform-api-7erqohmwxa-uc.a.run.app/**

Three tabs available:
- **📷 OCR Demo** - Extract text from images
- **⚙️ Run Workflow** - Execute YAML workflows with MCP adapter
- **🔧 MCP Tool Tester** - Call tools via JSON-RPC 2.0

### Option 2: Local Development

```bash
# Clone & install
git clone <repo-url> && cd agentic-platform
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ui && npm install && npm run dev &

# Backend
python3 -m uvicorn src.agentic_platform.api:app --port 8003

# Access at http://localhost:5173 (UI) or http://localhost:8003/docs (API)
```

### Option 3: Docker

```bash
docker build -t agentic-platform .
docker run -p 8080:8080 agentic-platform
# Visit http://localhost:8080
```

### Option 4: Google Cloud Run

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete setup guide with auto-scaling, monitoring, and CI/CD.

## 🛠️ API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check & API info |
| `/docs` | GET | Interactive API documentation |
| `/run-ocr/` | POST | Extract text from image |
| `/run-workflow/` | POST | Execute YAML workflow with tool adapter |
| `/mcp/tools` | GET | List available tools |
| `/mcp/request` | POST | Call tool via JSON-RPC 2.0 |

### Quick Examples

**OCR (Extract text from image)**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/run-ocr/ \
  -F "image=@document.jpg"
```

**Run Workflow (Execute YAML DAG)**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/run-workflow/ \
  -F "workflow=@workflow.yaml" \
  -F "input_artifact=@input.json" \
  -F "adapter=mcp"
```

**MCP Tool Call (JSON-RPC 2.0)**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "google_vision_ocr", "arguments": {"image_path": "doc.jpg"}},
    "id": 1
  }'
```

See [API.md](docs/api.md) for complete documentation with all examples.

## 🏗️ Architecture

The system consists of four main layers:

```
UI (React 18 + Material-UI)
        ↓ (HTTP/REST)
FastAPI Backend (MCP Server + REST Endpoints)
        ↓
Workflow Engine + Tool Registry + Audit Trail
        ↓
External Tools (Google Vision OCR, LangGraph, etc.)
```

**Core Components:**
- **Workflow Engine** - YAML DAG parser and executor
- **Tool Registry** - Plugin system for extensible tools
- **MCP Server** - JSON-RPC 2.0 protocol handler
- **Audit Trail** - Immutable event logging
- **Adapters** - Integration layers for external services

## 📂 Project Structure

```
agentic-platform/
├── src/agentic_platform/       # Core platform
│   ├── api.py                  # FastAPI app + MCP server
│   ├── workflow/               # Workflow engine
│   ├── tools/                  # Tool registry & Google Vision OCR
│   ├── adapters/               # External integrations
│   ├── audit/                  # Event logging
│   ├── agents/                 # Agent implementations
│   └── core/                   # Domain types & errors
├── ui/                         # React 18 + Material-UI frontend
├── tests/                      # 57+ comprehensive tests
│   ├── unit/                   # Unit tests
│   └── integration/            # End-to-end tests
├── docs/                       # Documentation & ADRs
├── demo_workflow.yaml          # Example YAML workflow
├── demo_input.json             # Example workflow input
├── Dockerfile                  # Multi-stage Docker build
├── cloudbuild.yaml             # Google Cloud Build config
└── requirements.txt            # Python dependencies
```

## ✅ Phase 8 Capabilities (Production Ready)

| Feature | Status | Details |
|---------|--------|---------|
| **OCR Engine** | ✅ | Google Vision API with confidence scoring |
| **MCP Server** | ✅ | JSON-RPC 2.0 compliance, tool discovery |
| **Workflow Engine** | ✅ | YAML DAG execution with branching |
| **Audit Trail** | ✅ | Immutable event logging with correlation IDs |
| **Cloud Deployment** | ✅ | Google Cloud Run with auto-scaling |
| **React UI** | ✅ | Material-UI dashboard with 3 demo tabs |
| **Test Coverage** | ✅ | 57+ tests covering all major features |

## 🧪 Testing & Quality

**Run Tests Locally**
```bash
pytest -v                           # All tests
pytest --cov=src tests/             # With coverage
pytest tests/unit/tools/            # Specific module
```

**Test Coverage:**
- 14 OCR tests ✅
- 22 MCP server tests ✅
- 22 MCP adapter tests ✅
- 13+ Workflow tests ✅
- 8+ Audit tests ✅
- **Total: 57+ tests (100% passing)**

## 🔧 Tech Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Frontend** | React 18, Material-UI 5, Vite | ✅ Production |
| **Backend** | Python 3.12, FastAPI, Pydantic v2 | ✅ Production |
| **OCR** | Google Cloud Vision API | ✅ Production |
| **Workflow** | YAML parser, DAG executor | ✅ Production |
| **MCP** | JSON-RPC 2.0, tool registry | ✅ Production |
| **Audit** | Immutable event log | ✅ Production |
| **Cloud** | Google Cloud Run, Cloud Build | ✅ Production |
| **CI/CD** | GitHub webhooks, Cloud Build | ✅ Production |
| **Testing** | pytest, coverage | ✅ Production |

## 🚢 Deployment

The application is deployed to Google Cloud Run with automatic CI/CD:

**Current Deployment**
- **URL:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/
- **Region:** us-central1
- **Memory:** 512Mi with auto-scaling
- **Build Time:** ~2-3 minutes
- **Status:** ✅ Live

**Deployment Pipeline**
```
Git Commit → Cloud Build → Docker Build → Cloud Run → Live ✅
                (auto)
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for manual deployment instructions and complete setup guide.

## 🔐 Security

- ✅ Immutable audit trails for compliance
- ✅ Input validation with Pydantic v2
- ✅ CORS protection per environment
- 🔄 OAuth 2.0 / OIDC (extensible)
- 📋 Google Cloud IAM service accounts

## 📄 License

MIT

---

**Built with ❤️ for AI-powered automation** | [Live Demo](https://agentic-platform-api-7erqohmwxa-uc.a.run.app/) | [Documentation](docs/)
