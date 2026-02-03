# 🤖 Agentic Platform

A production-ready, test-driven foundation for building multi-agent AI workflows with **OCR**, **MCP protocol**, **tool orchestration**, and **audit trails**. Currently at Phase 8 with live OCR capabilities and MCP integration—architected for future LLM agents, RAG systems, and enterprise AI applications.

**🌐 Live Demo:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/ | **📊 Tech Stack:** 28% of aspirational AI platform coverage | **🚀 Phase 9:** LangGraph Development (Week 1/4)

## ✨ Key Features

- **🏗️ Enterprise Architecture**: Modular design with adapter pattern, plugin system, and clean separation of concerns
- **🔌 MCP Server Integration**: Full Model Context Protocol support for extensible tool orchestration
- **🧪 Test-Driven Development**: 57+ passing tests with comprehensive coverage
- **📊 Audit & Compliance**: Immutable audit logs for every action, event tracking, and compliance reporting
- **☁️ Cloud-Ready**: Deployed to Google Cloud Run with auto-scaling, monitoring, and high availability
- **🎨 Modern UI**: React + Material-UI dashboard with real-time workflow execution and OCR demo
- **📚 Well-Documented**: Architecture Decision Records (ADRs), API docs, deployment guides

## ✨ Current Capabilities

### ✅ Production-Ready (Phase 8)
- **OCR Engine** - Google Vision API with intelligent confidence scoring (simple/complex/hard-to-read detection)
- **MCP Server** - Full JSON-RPC 2.0 compliance with tool registry and discovery
- **Workflow Engine** - YAML-based workflows with branching, retry policies, human review routing
- **Audit Trail** - Immutable event logging with correlation IDs and checksummed artifacts
- **Cloud Deployment** - Google Cloud Run with GitHub auto-trigger on every push
- **Modern UI** - React 18 + Material-UI dashboard with OCR demo and MCP tool tester
- **57+ Tests** - Comprehensive unit & integration test coverage with pytest

### 🔄 In Development
- **Agent Memory & State** - Multi-step conversation context (planned: PostgreSQL backend)
- **LLM Integration** - Model routing & provider selection (planned: Gemini, Claude, OpenAI)
  - **Phase 9 (Current):** LangGraph agent with real LLM support - Week 1/4 in progress
  - MockLLM for testing (no API costs)
  - Support for Claude, GPT-4, Gemini
- **RAG System** - Knowledge grounding and retrieval (planned: Pinecone/Weaviate)
- **Streaming UI** - Real-time token streaming and agent execution visualization
- **Multi-region** - Scaling beyond us-central1

### 🚀 Aspirational (Phase 9+)
- Enterprise security (OAuth, IAP, Secret Manager)
- Fine-tuning pipelines (LoRA, QLoRA)
- Distributed processing (PySpark, Dataflow)
- Advanced monitoring (LangSmith, W&B, Prometheus)
- Infrastructure as Code (Terraform, Helm)

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[READY_FOR_PRODUCTION.md](docs/READY_FOR_PRODUCTION.md)** | 🎯 **Start here** - Overview, interview guide, deployment checklist |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | ☁️ Google Cloud Run deployment guide |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | 💻 Development standards and guidelines |
| [CHECKLIST.md](docs/CHECKLIST.md) | ✅ Pre-deployment verification checklist |
| [**MCP.md**](docs/MCP.md) | Model Context Protocol implementation & integration |
| [**API.md**](docs/api.md) | REST API reference for all endpoints |
| [**Architecture.md**](docs/architecture.md) | System design and component overview |
| [**Adapters.md**](docs/adapters.md) | Tool registry and adapter patterns |
| [**Testing.md**](docs/testing.md) | Testing strategy and test coverage |
| [**Roadmap.md**](docs/roadmap.md) | TDD milestone history and project roadmap |
| [**Decisions**](docs/decisions/) | Architecture Decision Records (ADRs 1-10) |
| [**TECH_STACK_ANALYSIS.md**](TECH_STACK_ANALYSIS.md) | Gap analysis (28% current coverage) with roadmap |

## 🚀 Quick Start

### Option 1: Live Demo (No Setup Required)
Visit **https://agentic-platform-api-7erqohmwxa-uc.a.run.app/**

- ✅ **OCR Demo** - Upload images, extract text with confidence scoring (simple/complex/hard-to-read)
- ✅ **MCP Tool Tester** - Call registered tools directly with JSON-RPC (includes sample files for testing)
- ✅ **Workflow Executor** - Upload YAML workflow + JSON input, run with MCP or LangGraph adapter (see results below)
- ✅ **Full Audit Trail** - See all operations logged with timestamps and correlation IDs

### Option 2: Local Development

```bash
# Clone & setup
git clone <repo-url>
cd agentic-platform

# Backend setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ui && npm install && cd ..

# Start services
source .venv/bin/activate && python3 -m uvicorn src.agentic_platform.api:app --port 8003 &
cd ui && npx vite &

# Access:
# - UI: http://localhost:5173
# - API: http://localhost:8003
# - API Docs: http://localhost:8003/docs
```

### Option 3: Docker Deployment

```bash
# Build and run with Docker
docker build -t agentic-platform .
docker run -p 8080:8080 agentic-platform
# Visit http://localhost:8080
```

### Google Cloud Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for comprehensive Cloud Run deployment guide with:
- Step-by-step GCP setup
- Docker image building and pushing
- Cloud Run configuration
- Monitoring and auto-scaling
- Security best practices

# Run container
docker run -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  agentic-platform

# Visit http://localhost:8080
```

## 🛠️ API Endpoints

| Method | Endpoint | Purpose | What You Get |
|--------|----------|---------|--------------|
| GET | `/` | Welcome & health check | - |
| GET | `/docs` | Interactive Swagger docs | - |
| GET | `/mcp/tools` | List all available tools | Tool names, descriptions, input schemas |
| POST | `/mcp/request` | Call a tool (JSON-RPC 2.0) | Tool output (OCR text + confidence, etc.) |
| POST | `/run-ocr/` | Extract text from image | Text, confidence score, symbol count |
| POST | `/run-workflow/` | Execute workflow DAG | **Job results** + **tool outputs** + **audit trail** |

### Quick API Examples

**OCR with Confidence Scoring**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/run-ocr/ \
  -F "image=@document.jpg"

# Response: {
#   "text": "...",
#   "confidence": 1.0,              # 1.0 = simple, 0.95 = complex layout, 0.2-0.4 = hard-to-read
#   "confidence_source": "default_simple_layout",
#   "symbols_count": 150
# }
```

**MCP Tool Discovery**
```bash
curl https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/tools

# Response: {
#   "tools": [
#     { "name": "google_vision_ocr", "description": "...", "inputSchema": {...} }
#   ]
# }
```

**MCP Tool Call (JSON-RPC)**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "document.jpg"}
    },
    "id": 1
  }'
```

**Workflow Execution**
```bash
# Create workflow.yaml (YAML DAG with nodes and edges)
cat > workflow.yaml << 'EOF'
nodes:
  - id: start
    type: start
  - id: ocr_step
    type: tool
    tool: google_vision_ocr
    model: default
  - id: end
    type: end
edges:
  - from: start
    to: ocr_step
  - from: ocr_step
    to: end
EOF

# Create input.json (input data for workflow)
cat > input.json << 'EOF'
{"image_path": "document.jpg"}
EOF

# Execute workflow
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/run-workflow/ \
  -F "workflow=@workflow.yaml" \
  -F "input_artifact=@input.json" \
  -F "adapter=mcp"

# Response:
# {
#   "result": {
#     "job_id": "job-1",
#     "status": "completed",
#     "tool_results": [...]
#   },
#   "tool_results": [...],      # Output from each tool in workflow
#   "audit_log": [...]          # Complete audit trail with timestamps
# }
```

See [API.md](docs/api.md) for full endpoint documentation with more examples.

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│  UI (React 18 + Material-UI)            │
│  - OCR Text Extractor                   │
│  - MCP Tool Tester                      │
│  - Workflow Executor                    │
└────────────────┬─────────────────────────┘
                 │ (HTTP/REST + WebSocket)
                 ▼
┌──────────────────────────────────────────┐
│  FastAPI Backend                         │
│  ├─ REST Endpoints                       │
│  ├─ MCP Server (JSON-RPC 2.0)           │
│  ├─ OCR Workflow Integration             │
│  └─ Audit Event Emitter                  │
└────┬──────────────────┬──────────┬────────┘
     │                  │          │
     ▼                  ▼          ▼
┌──────────────┐ ┌────────────┐ ┌──────────────┐
│ Workflow     │ │ Tool       │ │ Audit        │
│ Engine       │ │ Registry   │ │ Trail        │
│              │ │            │ │              │
│ - Parser     │ │ - MCP      │ │ - Logger     │
│ - Executor   │ │ - Discovery│ │ - Events     │
│ - Branching  │ │ - Routing  │ │ - Immutable  │
└──────────────┘ └────────────┘ └──────────────┘
     │                  │
     └────────┬─────────┘
              ▼
┌──────────────────────────────────────────┐
│  Adapters & Tools                        │
│  ├─ Google Vision OCR (✅ Prod)         │
│  ├─ MCP Client Adapter (✅ Prod)        │
│  ├─ LangGraph Adapter (🔄 Stub)         │
│  ├─ S3 Artifact Store                   │
│  ├─ Database Artifact Store              │
│  └─ SaaS Tool Adapter                    │
└──────────────────────────────────────────┘
```

## 📂 Project Structure

```
agentic-platform/
├── src/agentic_platform/          # Core platform
│   ├── api.py                     # FastAPI app + MCP server
│   ├── cli.py                     # CLI interface
│   ├── workflow/                  # Workflow engine & parser
│   │   ├── definition.py          # YAML parsing
│   │   └── engine.py              # Execution engine
│   ├── tools/                     # Tool registry & policies
│   │   ├── tool_registry.py       # Tool discovery
│   │   ├── google_vision_ocr.py   # OCR adapter (14 tests ✅)
│   │   ├── model_router.py        # Model selection
│   │   └── policy.py              # Policy enforcement
│   ├── adapters/                  # External integrations
│   │   ├── mcp_adapter.py         # MCP JSON-RPC client
│   │   ├── langgraph_adapter.py   # LangGraph (stub)
│   │   ├── s3_artifact_store.py   # Cloud Storage
│   │   └── saas_tool_adapter.py   # 3rd-party tools
│   ├── audit/                     # Event logging
│   │   ├── audit_log.py           # Immutable log
│   │   └── events.py              # Event types
│   ├── agents/                    # Agent implementations
│   │   ├── base.py                # Base agent class
│   │   └── registry.py            # Agent registry
│   └── core/                      # Domain types
│       ├── types.py               # Data models
│       ├── errors.py              # Error types
│       └── ids.py                 # ID generation
├── ui/                            # React frontend
│   ├── src/
│   │   ├── App.jsx                # Main UI
│   │   └── components/            # React components
│   └── package.json
├── tests/                         # 57+ comprehensive tests
│   ├── unit/                      # Unit tests by module
│   └── integration/               # End-to-end tests
├── docs/                          # Complete documentation
│   ├── roadmap.md                 # Phase 0-8 + 12-week plan
│   ├── architecture.md            # System design
│   ├── api.md                     # API reference
│   ├── deployment.md              # Cloud Run setup
│   └── decisions/                 # Architecture Decision Records
└── TECH_STACK_ANALYSIS.md         # Gap analysis (28% coverage)
```

## ✅ Phase 8 Capabilities

### OCR Engine (Production ✅)
- Google Vision API integration with intelligent confidence scoring
- Three confidence levels:
  - **1.0** - Simple documents (< 150 symbols, high quality)
  - **0.95** - Complex layouts (> 150 symbols, tables/forms)
  - **0.2-0.4** - Hard-to-read (averaged from individual symbol scores)
- Confidence source tracking for debugging
- 14 comprehensive tests (all passing)

### MCP Server (Production ✅)
- Full JSON-RPC 2.0 protocol compliance
- Tool discovery with `/mcp/tools` endpoint
- Tool invocation with `/mcp/request` endpoint
- 22 MCP server tests + 22 client adapter tests
- 13 end-to-end integration tests

### Workflow Engine (Production ✅)
- YAML-based workflow definitions (nodes + edges DAG)
- Node-edge graph execution with cycle detection
- Conditional branching (evaluate conditions on edges)
- Retry policies and error handling
- Human-in-the-loop review routing (for low-confidence results)
- Artifact versioning and checksumming
- **View Results:** Job status, tool outputs from each node, and complete audit trail with timestamps

### Audit Trail (Production ✅)
- Immutable event logging with timestamps
- Correlation IDs for tracing workflows
- Artifact checksumming and artifact store linking
- Complete execution history

### Cloud Deployment (Production ✅)
- Google Cloud Run with auto-scaling
- GitHub webhook triggers (automatic on push)
- Cloud Build integration
- Live at: https://agentic-platform-api-7erqohmwxa-uc.a.run.app/

## 🧪 Testing & Quality

**Run Tests Locally**
```bash
# All tests with verbose output
pytest -v

# With coverage report
pytest --cov=src --cov-report=html tests/

# Watch mode (auto-rerun on changes)
pytest-watch

# Specific test file
pytest tests/unit/tools/test_google_vision_ocr.py -v
```

**Test Coverage (Phase 8)**
- **14 OCR tests** - Confidence scoring, symbol averaging, layout detection ✅
- **22 MCP server tests** - Protocol compliance, error handling ✅
- **22 MCP adapter tests** - HTTP client, tool discovery ✅
- **13 Workflow tests** - Branching, retry, human review ✅
- **8+ Audit tests** - Event immutability, correlation ✅
- **Total: 57+ tests passing** ✅ (100%)

## 🔧 Tech Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Frontend** | React 18, Material-UI 5, Vite, TypeScript | ✅ Production |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, Uvicorn | ✅ Production |
| **OCR** | Google Cloud Vision API | ✅ Production |
| **Workflow** | YAML parser, DAG executor, branching logic | ✅ Production |
| **MCP** | JSON-RPC 2.0, tool registry, discovery | ✅ Production |
| **Audit** | Immutable event log, checksumming | ✅ Production |
| **Cloud** | Google Cloud Run, Cloud Build | ✅ Production |
| **CI/CD** | GitHub webhooks, Cloud Build triggers | ✅ Production |
| **Testing** | pytest, pytest-cov, pytest-watch | ✅ Production |
| **Standards** | JSON-RPC 2.0, OpenAPI 3.0, MCP 1.0 | ✅ Full |

**Coverage Analysis:** 20/70 AI platform categories implemented (28%) | See [TECH_STACK_ANALYSIS.md](TECH_STACK_ANALYSIS.md)

## 🚢 Deployment

**Automatic Deployment Pipeline**
```
GitHub Commit → Cloud Build Trigger → Docker Build → Cloud Run Deploy
                                        (auto on push)      (live immediately)
```

**Current Deployment**
- **URL:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/
- **Region:** us-central1 (us-east1 planned for multi-region)
- **Memory:** 512Mi (auto-scaling enabled)
- **Build Time:** ~3 minutes
- **Status:** ✅ Live and operational

**Manual Deployment**
See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed setup instructions.

```bash
# Deploy to Cloud Run (requires gcloud CLI)
gcloud builds submit --config=cloudbuild.yaml

# Monitor build
gcloud builds log -f

# View logs
gcloud run logs read agentic-platform-api --limit=50
```

## 🔐 Security & Compliance

- ✅ **Immutable Audit Trails** - All operations logged with timestamps and correlation IDs
- ✅ **Checksummed Artifacts** - Artifact integrity validated on every access
- ✅ **PII Redaction** - Middleware support for sensitive data masking
- ✅ **CORS Protection** - Configured per environment
- ✅ **Input Validation** - Pydantic v2 for strict type checking
- 🔄 **Token-based Auth** - Extensible for OAuth 2.0/OIDC (not yet required)
- 📋 **Service Accounts** - IAM policies via Google Cloud
- 📋 **Secret Management** - Path for integration with Google Secret Manager

## 📈 Development Roadmap

### Completed (Phase 0-8)
- ✅ **Phase 0** - Bootstrap + core types
- ✅ **Phase 1** - Audit trail with immutable events
- ✅ **Phase 2** - Tool interface + mocking
- ✅ **Phase 3** - Workflow engine with branching
- ✅ **Phase 4** - Agent registry + artifact store
- ✅ **Phase 5** - End-to-end OCR MVP
- ✅ **Phase 5.5** - Model selection routing
- ✅ **Phase 6** - Google Vision OCR integration
- ✅ **Phase 7** - MCP Server integration (57 tests)
- ✅ **Phase 8** - OCR confidence improvements (14 tests, deployed)

### Current Plans (Phase 9+)
See [Roadmap.md](docs/roadmap.md) for full TDD history and 12-week tech stack expansion:

| Weeks | Focus | Goals | Impact |
|-------|-------|-------|--------|
| 1-2 | **LLM Foundation** | Vertex AI, model router, cost tracking | 🔴 Critical |
| 3-4 | **Agent Memory** | PostgreSQL state store, conversation history | 🔴 Critical |
| 5-6 | **RAG System** | Pinecone/Weaviate, embeddings, chunking | 🔴 Critical |
| 7-8 | **Streaming UI** | SSE tokens, execution traces, tool viz | 🟡 High |
| 9-10 | **Observability** | Cloud Logging, LangSmith, metrics | 🟡 High |
| 11-12 | **Infrastructure** | Terraform, Helm, Prometheus, canaries | 🟢 Medium |

**Progress:** 28% of aspirational AI platform tech stack (20/70 categories) | Target: 80%+ in 12 weeks

## 🔗 Integration Examples

### Python Client
```python
import requests

# Call OCR via MCP
response = requests.post(
    'https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request',
    json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'google_vision_ocr',
            'arguments': {'image_path': 'document.jpg'}
        },
        'id': 1
    }
)

result = response.json()
print(f"Text: {result['result']['text']}")
print(f"Confidence: {result['result']['confidence']}")
```

### JavaScript Client
```javascript
// Call OCR via MCP
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
        arguments: { image_path: 'document.jpg' }
      },
      id: 1
    })
  }
);

const result = await response.json();
console.log(`Text: ${result.result.text}`);
console.log(`Confidence: ${result.result.confidence}`);
```

### Curl (Simplest)
```bash
# Get list of available tools
curl https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/tools | jq

# Call a tool
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request \
  -H 'Content-Type: application/json' \
  -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"google_vision_ocr\",\"arguments\":{\"image_path\":\"doc.jpg\"}},\"id\":1}'
```

## 📄 License

MIT

---

**Built with ❤️ for AI-powered automation** | [Live Demo](https://agentic-platform-api-7erqohmwxa-uc.a.run.app/) | [Docs](docs/)
