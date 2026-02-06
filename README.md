# 🤖 Agentic Platform

A test-driven, extensible foundation for building AI workflows with **OCR**, **MCP protocol**, **tool orchestration**, and **audit trails**. Currently Phase 8 complete with ongoing Phase 9 (LangGraph agent orchestration).

**🌐 Live Demo:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/ | **✅ Status:** Phase 8 Complete | **🔄 Phase 9:** LangGraph (In Progress)

## 🛠️ Tech Stack Strategy
**Core Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn (ASGI)  
**Frontend**: React 18, TypeScript, Vite, Material UI v5  
**AI & Agentic Frameworks**: LangChain (Core), LangGraph (Stateful Agents), MCP 1.0 (JSON-RPC), Google Cloud Vision API  
**Enterprise Integration**: Provider Pattern, Multi-Tenancy (`TenantContext`), Mock & Enterprise Adapters  
**Infrastructure**: Google Cloud Run (Serverless), Cloud Build (CI/CD), Docker  
**Future Stack (Planned)**: Pinecone/Weaviate (Vector DB), PostgreSQL+RLS (State), OpenTelemetry (Observability)

## ✨ Currently Implemented (Phase 8 ✅)

- **🏗️ Enterprise Architecture** - Adapter pattern, clean separation, plugin system for extensibility
- **🔌 MCP Server** - Full JSON-RPC 2.0 protocol for standardized tool access
- **📄 OCR Engine** - Google Vision API with confidence scoring
- **⚙️ Workflow Engine** - YAML DAGs with branching, retry, conditional logic
- **📊 Audit Trail** - Immutable event logging with correlation IDs
- **🎨 Modern UI** - React + Material-UI (OCR demo, MCP tester, workflow runner)
- **🧪 Testing** - 57+ passing tests (unit, integration, E2E)
- **☁️ Cloud Deployment** - Google Cloud Run with auto-scaling and GitHub CI/CD

## ⚠️ Known Limitations

- **State Persistence** - In-memory only (PostgreSQL integration in Phase 10)
- **Authentication/Authorization** - Not yet implemented (Phase 10)
- **LangGraph Agent** - Stub only, returns simulated responses (Phase 9 in progress)
- **No LLM Integration** - LLM factory built, real agent implementation pending
- **No RAG System** - Planned for Phase 12
- **No Real-Time Streaming** - Planned for Phase 12

## 🚀 Roadmap

| Phase | Focus | Status | Target |
|-------|-------|--------|--------|
| **Phase 8** | OCR, MCP, Workflows | ✅ Complete | Feb 2026 |
| **Phase 9** | LangGraph Agent | 🔄 In Progress | Feb 28 |
| **Phase 10** | PostgreSQL, Auth, Security | 📋 Planned | Apr 1 |
| **Phase 11** | Observability, Monitoring | 📋 Planned | May 1 |
| **Phase 12** | RAG, Streaming, Global Scale | 📋 Planned | Jun 1 |

See [docs/roadmap.md](docs/roadmap.md) for detailed implementation plan.

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

## 🔧 Technologies

**Backend:**
- Python 3.12
- FastAPI (REST API)
- Pydantic v2 (data validation)
- Uvicorn (ASGI server)
- google-cloud-vision (OCR)
- PyYAML (workflow parsing)
- python-multipart (file uploads)
- LangChain (Phase 9: LLM integration)

**Frontend:**
- React 18
- Material-UI 5
- Vite (build tool)

**Cloud Infrastructure:**
- Google Cloud Run (serverless hosting)
- Google Cloud Build (CI/CD)
- Google Cloud Vision API (OCR)

**Standards & Protocols:**
- JSON-RPC 2.0 (MCP transport)
- OpenAPI 3.0 (API documentation)
- MCP 1.0 (Model Context Protocol)

**Testing & Quality:**
- pytest (test framework)
- pytest-cov (coverage reports)

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
