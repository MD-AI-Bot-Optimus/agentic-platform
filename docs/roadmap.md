57. feat: minimal CLI for running workflows from YAML/JSON
58. feat: minimal REST API for workflow execution (FastAPI)
56. test: integration test for artifact storage (S3 adapter, audit log linkage)
55. test: integration test for error handling (adapter failure, audit log error event)
54. test: integration test for branching workflow (conditional edges)
# Agentic Platform Roadmap

**Current Status:** Phase 8 Complete | **Live Deployment:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app/ | **Test Coverage:** 57+ tests (100% passing)

This document details the test-driven development (TDD) roadmap and complete development history. Phases 0-8 are production-ready with comprehensive test coverage. Phase 9 outlines the 12-week technology stack expansion to build a full AI/LLM/agentic platform.

---

## Executive Summary

### What Works Today (Phase 8 ✅)
- **OCR** - Google Vision API with intelligent confidence scoring (simple/complex/hard-to-read)
- **MCP** - Full JSON-RPC 2.0 server with tool discovery and invocation
- **Workflows** - YAML-based DAG execution with branching and retry policies
- **Audit** - Immutable event logging with checksummed artifacts
- **Deployment** - Cloud Run with GitHub auto-trigger
- **Testing** - 57+ comprehensive tests (all passing)

### What's Planned (Phase 9+ 🚀)
1. **Weeks 1-2:** LLM integration (Vertex AI, Claude, GPT-4)
2. **Weeks 3-4:** Agent state & memory (PostgreSQL, conversation history)
3. **Weeks 5-6:** RAG system (vector DB, embeddings, retrieval)
4. **Weeks 7-8:** Streaming UI (token streaming, execution traces)
5. **Weeks 9-10:** Observability (logging, monitoring, LangSmith)
6. **Weeks 11-12:** Infrastructure (Terraform, Helm, scaling)

**Progress:** 28% of aspirational tech stack implemented | **Target:** 80%+ coverage in 12 weeks

## Phase 0 — Bootstrap & Core Domain
**Goal:** Establish foundation with core types and immutable IDs  
**Status:** ✅ Complete (4 commits)

1. chore: init repo with pyproject, src layout, pytest
2. test: add failing test for JobId + CorrelationId generation
3. feat: add core id utilities
4. feat: implement core domain dataclasses + validation

## Phase 1 — Audit Trail & Event Logging
**Goal:** Immutable event logging for compliance  
**Status:** ✅ Complete (3 commits)

6. test: audit log emits start/end events for a step
7. feat: in-memory audit log
8. feat: audit event model + immutability contract

## Phase 2 — Tool Registry & Protocol
**Goal:** Tool discovery system with deterministic mocking  
**Status:** ✅ Complete (5 commits)

11. test: tool registry can list and call tools
12. feat: tool protocol + tool registry
13. test: fake tool client simulates external tools deterministically
14. feat: implement FakeToolClient
15. feat: tool error schema + validation

## Phase 3 — Workflow Engine & Execution
**Goal:** DAG-based workflow execution with branching  
**Status:** ✅ Complete (9 commits)

17. test: parse workflow definition from YAML
18. feat: workflow definition parser + validator
19. test: engine executes single-node workflow
20. feat: workflow engine minimal runner
21. test: engine supports conditional branching
22. feat: implement branching conditions
23. test: engine retries node on transient failure
24. feat: implement retry policy
25. feat: add human-in-loop state + routing

## Phase 4 — Agent Architecture & Artifact Store
**Goal:** Versioned agents with checksummed artifacts  
**Status:** ✅ Complete (8 commits)

27. test: agent registry registers versioned agents
28. feat: implement agent registry (in-memory)
29. test: agent node calls tool client and writes artifact
30. feat: implement artifact store (in-memory)
31. feat: implement base Agent and ToolCallingAgent
32. feat: artifact hashing + versioning
33. feat: artifact audit linking
34. refactor: separate workflow node executor from engine


## Phase 5 — OCR MVP & Model Routing
**Goal:** End-to-end OCR workflow with model selection  
**Status:** ✅ Complete (8 commits)

**5a - Core MVP**
35. ✅ test: end-to-end OCR MVP happy path
36. ✅ feat: OCR MVP workflow YAML
37. ✅ feat: fake tool fixtures for OCR flow
38. ✅ feat: review queue as state + artifact
39. ✅ feat: resume token + state hydration
40. ✅ chore: CLI runner + JSON output

**5b - Model Selection (Phase 5.5)**
41. test: model selection per node/task
42. feat: implement ModelRouter for routing tool calls to specific models
43. feat: fallback/default model selection logic
44. docs: update architecture and usage for model selection

## Phase 6 — Google Vision OCR Integration
**Goal:** Production OCR with Google Cloud Vision API  
**Status:** ✅ Complete (8 commits)

47. ✅ test: OCR integration end-to-end
48. ✅ feat: GoogleVisionOCR adapter (Application Default Credentials)
49. ✅ feat: `/run-ocr/` FastAPI endpoint (multipart form)
50. ✅ feat: OCR workflow YAML (ocr_mvp.yaml)
51. ✅ feat: React OCR demo component (upload + results)
52. ✅ feat: formatted text output (line-by-line display)
53. ✅ docs: OCR architecture + authentication
54. ✅ chore: Google Cloud SDK setup + project config

## Phase 7 — MCP Server Integration
**Goal:** Full JSON-RPC 2.0 Model Context Protocol support  
**Status:** ✅ Complete (81 commits, 57 tests)

**7a - Protocol & Server**
55. ✅ test: MCPServer JSON-RPC 2.0 (22 unit tests)
56. ✅ feat: MCPServer handler (tools/list, tools/call)
57. ✅ feat: FastAPI /mcp/request + /mcp/tools endpoints
58. ✅ test: MCPAdapter HTTP client (22 unit tests)
59. ✅ feat: MCPAdapter for remote MCP servers

**7b - Integration & UI**
60. ✅ test: End-to-end MCP workflow (13 integration tests)
61. ✅ test: OCR tool calling via MCP
62. ✅ feat: React MCP Tool Tester UI
63. ✅ feat: Tool discovery from /mcp/tools
64. ✅ docs: ADR-010 MCP Server Integration
65. ✅ docs: Comprehensive MCP Implementation Guide
66. ✅ chore: 57 total tests passing (all green)

## Phase 8 — OCR Confidence Improvements
**Goal:** Intelligent confidence scoring for OCR quality assessment  
**Status:** ✅ Complete (91 commits, 14 tests added)

**8a - Confidence Mechanism**
67. ✅ test: OCR confidence for simple documents (1.0)
68. ✅ test: OCR confidence for hard-to-read documents (0.2-0.4 avg)
69. ✅ test: OCR confidence for complex layouts (>150 symbols = 0.95)

**8b - Implementation & Fixes**
70. ✅ feat: Layout complexity detection (initial threshold: 50)
71. ✅ feat: Confidence source tracking for debugging
72. ✅ fix: Increase threshold from 50 to 150 symbols (false positives)
73. ✅ test: 14 comprehensive OCR confidence tests (all passing)
74. ✅ docs: Updated OCR endpoint documentation
75. ✅ docs: Updated architecture documentation
76. ✅ docs: Updated adapter documentation
77. ✅ docs: Updated API documentation
78. ✅ docs: Updated roadmap with Phase 8 completion
79. ✅ chore: Remove obsolete test files (DEPLOYMENT_TEST.md)

**8c - Deployment**
80. ✅ feat: GitHub webhook trigger (fixed from GitLab)
81. ✅ feat: Cloud Build auto-deploy pipeline
82. ✅ test: Verified confidence values (letter=1.0, handwriting=1.0, stock=0.95)
83. ✅ docs: Updated DEPLOYMENT.md with GitHub process

## CURRENT STATUS

**Live Deployment:** https://agentic-platform-api-7erqohmwxa-uc.a.run.app

**Implemented Features:**
- ✅ OCR with intelligent confidence scoring
- ✅ MCP protocol support (JSON-RPC 2.0)
- ✅ Google Vision API integration
- ✅ React UI with MCP Tool Tester
- ✅ Workflow engine with branching
- ✅ Audit logging
- ✅ Cloud Run deployment with GitHub auto-trigger

**Known Limitations:**
- ❌ LangGraph: Stub only (returns simulated responses, no real graph execution)
- ❌ No LLM integration (no Claude, GPT-4, etc.)
- ❌ No RAG/vector database
- ❌ No persistent state (in-memory only)
- ❌ No agent memory/conversation history

**Next Priorities:**
1. LangGraph real implementation (need dependencies: langgraph, langchain, anthropic)
2. LLM integration for agentic workflows
3. RAG system for knowledge grounding
4. Persistent state store (PostgreSQL)

---

## Phase 9 — LangGraph Agent Orchestration (In Development)

**Goal:** Convert LangGraph stub to production-grade agent with LLM reasoning, tool use, and memory  
**Status:** 🔄 Week 1/4 In Progress | **Start Date:** Feb 2, 2026 | **Target:** Feb 28, 2026

**Phase 9 Detailed Plan & Progress:** See [LANGGRAPH_DEVELOPMENT_PLAN.md](LANGGRAPH_DEVELOPMENT_PLAN.md) and [LANGGRAPH_PROGRESS.md](LANGGRAPH_PROGRESS.md)

### Week 1: Setup & Dependencies (Feb 2-8) 🔄 IN PROGRESS

**✅ Completed:**
- ✅ Added LangGraph, LangChain, and LLM provider dependencies
- ✅ Created .env.example with all configuration options
- ✅ Built LLM provider factory (Anthropic, OpenAI, Google, Mock)
- ✅ Implemented MockLLM for deterministic testing
- ✅ Defined AgentState schema for LangGraph state machine

**⏳ In Progress:**
- [ ] Test dependency installations
- [ ] Create LLM configuration documentation
- [ ] Set up environment variable loading

**📋 Planned (Weeks 2-4):**
1. Core LangGraph agent implementation (tool use, reasoning)
2. Comprehensive test coverage (25+ tests)
3. Agent memory and conversation history
4. Integration with existing workflow engine
5. Cloud deployment with real LLM providers
6. Documentation and examples

---

## Phase 10 — Enterprise Foundation (Persistence & Security)

**Goal:** Add persistent state, authentication, authorization, and production security  
**Status:** 📋 Planned | **Target Duration:** 4-6 weeks | **Target Start:** Mar 1, 2026

### Enterprise Readiness Assessment
**Current Score: 60% (6.5/10)**
- ✅ Architecture (9/10) - Excellent adapter pattern foundation
- ✅ Extensibility (9/10) - Plugin system, clean separation
- ✅ Core Features (8/10) - OCR, MCP, Workflows working
- ❌ Data Persistence (2/10) - In-memory only
- 🔄 LLM/Agents (5/10) - Phase 9 in progress
- ✅ DevOps/Deployment (7/10) - Cloud Run operational
- ❌ Security (4/10) - No auth/authz
- ✅ Documentation (8/10) - Comprehensive

### Week 1-2: Persistent State Layer
- [ ] Add PostgreSQL integration (schema + migrations)
- [ ] Implement ArtifactStore with S3 + DB fallback
- [ ] Add workflow run history persistence
- [ ] Implement agent conversation history storage
- [ ] Create database initialization scripts
- **Impact:** Enables multi-session workflows and audit compliance

### Week 2-3: Authentication & Authorization
- [ ] Add JWT token support (issuer, validation, refresh)
- [ ] Implement RBAC (role-based access control)
- [ ] Add API key management (CRUD, rate limiting)
- [ ] Create user/organization management endpoints
- [ ] Add OAuth2 integration hooks (Auth0, Google)
- **Impact:** Enables multi-tenant deployments and compliance

### Week 3-4: Secrets & Configuration Management
- [ ] Integrate Google Cloud Secret Manager
- [ ] Add environment-specific config (dev/staging/prod)
- [ ] Implement secret rotation policies
- [ ] Create configuration schema validation
- [ ] Add .env.secure pattern with vault support
- **Impact:** Production-grade secrets handling

### Week 4-5: Advanced Security
- [ ] Add request signing and verification
- [ ] Implement rate limiting per user/API key
- [ ] Add CORS and CSRF protection
- [ ] Create PII redaction policies (audit-safe)
- [ ] Add input validation middleware
- **Impact:** Hardens API against attacks

### Week 5-6: Infrastructure as Code
- [ ] Create Terraform modules (compute, database, secrets)
- [ ] Add Helm charts for Kubernetes deployment
- [ ] Implement CloudSQL backup policies
- [ ] Add multi-region/HA deployment configs
- [ ] Create deployment CI/CD pipeline
- **Impact:** Reproducible, scalable deployments

**Success Criteria:**
- 100% of existing tests pass with PostgreSQL backend
- API operations require valid JWT or API key
- Zero plaintext secrets in repos/logs
- Deployments reproducible with IaC
- Documentation covers self-hosted setup

---

## Phase 11 — Observability & Enterprise Operations

**Goal:** Production-grade monitoring, logging, tracing, and operational excellence  
**Status:** 📋 Planned | **Target Duration:** 4 weeks | **Target Start:** Apr 1, 2026

### Week 1-2: Centralized Logging & Metrics
- [ ] Integrate Cloud Logging (structured JSON logs)
- [ ] Add Prometheus metrics (latency, errors, throughput)
- [ ] Implement distributed tracing (OpenTelemetry)
- [ ] Create monitoring dashboard (Cloud Monitoring/Grafana)
- [ ] Add cost tracking per operation
- **Impact:** Full operational visibility

### Week 2-3: LLM Observability
- [ ] Integrate LangSmith for LLM tracing
- [ ] Add token counting and cost per request
- [ ] Implement prompt versioning audit
- [ ] Create LLM performance dashboard
- [ ] Add model selection analytics
- **Impact:** LLM-specific insights and optimization

### Week 3-4: Alerting & Incident Response
- [ ] Setup error budget policies
- [ ] Create automated alert rules (latency, errors, cost)
- [ ] Add incident tracking integration (PagerDuty)
- [ ] Create runbooks for common issues
- [ ] Implement SLO/SLA tracking
- **Impact:** Proactive issue detection and response

**Success Criteria:**
- Logs centralized and searchable
- Dashboards covering all metrics
- Alerts trigger before SLO breach
- 99.9% uptime tracking
- Cost optimization insights

---

## Phase 12 — Advanced Features & Scaling

**Goal:** RAG integration, advanced agent capabilities, global scaling  
**Status:** 📋 Aspirational | **Target Start:** May 1, 2026

### Week 1-2: RAG System
- [ ] Add vector database (Pinecone/Weaviate)
- [ ] Implement embedding pipeline (Sentence Transformers)
- [ ] Add semantic chunking for documents
- [ ] Create retrieval-augmented workflow node
- [ ] Build knowledge base management UI
- **Impact:** Grounds agents in proprietary knowledge

### Week 2-3: Streaming & Real-Time UI
- [ ] Implement Server-Sent Events (SSE) for token streaming
- [ ] Add execution trace visualization
- [ ] Create tool call inspector UI
- [ ] Build prompt playground
- [ ] Add real-time collaboration features
- **Impact:** Transforms UX for interactive workflows

### Week 3-4: Global Scaling & Performance
- [ ] Implement request caching (Redis)
- [ ] Add CDN integration for static assets
- [ ] Create multi-region deployment strategy
- [ ] Optimize database queries (indexing, connection pooling)
- [ ] Add performance testing suite (k6/Artillery)
- **Impact:** Sub-100ms latencies, global availability

**End State (Phase 12 Complete):**
- ✅ Full LangGraph agent orchestration
- ✅ Enterprise-grade persistence and security
- ✅ Production observability and monitoring
- ✅ RAG-powered knowledge grounding
- ✅ Real-time streaming UI
- ✅ Global, scalable infrastructure
- **Enterprise Readiness Score: 95%** (9.5/10)

---

## Technology Stack Expansion (Detailed Roadmap)

### Coverage Summary
- **Phase 8 Complete:** 20/70 tech stack categories (28%)
- **Phase 9 (LangGraph):** +15 categories (42%)
- **Phase 10 (Enterprise):** +18 categories (67%)
- **Phase 11 (Observability):** +12 categories (85%)
- **Phase 12 (Advanced):** +10 categories (95%+)
- **Not Implemented:** 47/70 (67%)

### Week 1-2: LLM Foundation
- [ ] Add Vertex AI SDK (google-cloud-aiplatform)
- [ ] Implement model router (Gemini, Claude, OpenAI)
- [ ] Add token counting and cost tracking
- [ ] Create LLM model selection UI
- **Impact:** Unlocks core AI agent capabilities

### Week 3-4: Agent State & Memory
- [ ] Add PostgreSQL integration (state store)
- [ ] Implement conversation history storage
- [ ] Add workflow persistence
- [ ] Create agent execution history API
- **Impact:** Makes agents stateful and context-aware

### Week 5-6: RAG System
- [ ] Add Pinecone/Weaviate integration
- [ ] Implement embedding pipeline (Sentence Transformers)
- [ ] Add semantic chunking
- [ ] Build retrieval-augmented workflow
- **Impact:** Grounds agents in knowledge base

### Week 7-8: Frontend Streaming & Visualization
- [ ] Implement SSE for token streaming UI
- [ ] Add agent execution trace viewer
- [ ] Create tool call visualization
- [ ] Build prompt playground
- [ ] Add chat history management UI
- **Impact:** Significantly improves UX for complex interactions

### Week 9-10: Observability & Monitoring
- [ ] Integrate Cloud Logging
- [ ] Add Cloud Monitoring and metrics
- [ ] Connect LangSmith for LLM tracing
- [ ] Implement cost/token tracking dashboard
- **Impact:** Production-grade visibility and governance

### Week 11-12: Infrastructure & MLOps
- [ ] Add Terraform configurations (IaC)
- [ ] Implement Helm charts for Kubernetes
- [ ] Setup Prometheus/Grafana monitoring
- [ ] Add experiment tracking framework
- [ ] Setup canary deployments
- **Impact:** Enterprise-ready infrastructure

### Priority Features by Impact

**HIGH IMPACT (Do First):**
1. LLM Integration - Enables actual AI reasoning
2. Agent Memory Store - Makes agents conversational
3. RAG Pipeline - Adds knowledge grounding
4. Token Streaming UI - Transforms UX

**MEDIUM IMPACT (Do Next):**
5. Cost Tracking - Critical for production
6. Execution Traces - Essential for debugging
7. PostgreSQL State Store - Enables persistence
8. Multi-model Selection - Supports hybrid deployments

**LOWER IMPACT (Enhancement):**
9. Fine-tuning capabilities
10. Distributed processing (PySpark)
11. Advanced monitoring (Prometheus)
12. Infrastructure as Code

### Quick Wins (This Week)

**1. Add Server-Sent Events for Response Streaming**
```python
from fastapi.responses import StreamingResponse

@app.post("/stream-ocr")
async def stream_ocr_results():
    async def generate():
        for chunk in ocr_response:
            yield json.dumps(chunk) + "\n"
    return StreamingResponse(generate())
```

**2. Add WebSocket for Real-time Agent Execution**
```python
@app.websocket("/ws/agent/{agent_id}")
async def websocket_agent(agent_id: str, websocket: WebSocket):
    await websocket.accept()
    # Stream agent steps in real-time
```

**3. Integrate Vertex AI Generative Models**
```python
# Add to requirements
# google-cloud-aiplatform
# google-generativeai

from vertexai.generative_models import GenerativeModel
model = GenerativeModel("gemini-1.5-pro")
```

**4. Add Code Coverage Tracking**
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Technology Gaps to Address

| Category | Status | Impact |
|----------|--------|--------|
| LLM Providers | ❌ Not Started | 🔴 Critical |
| Vector Database | ❌ Not Started | 🔴 Critical |
| Agent Memory | ❌ Not Started | 🔴 Critical |
| Streaming UI | ❌ Not Started | 🟡 High |
| Observability | ❌ Not Started | 🟡 High |
| Infrastructure as Code | ❌ Not Started | 🟢 Medium |
| Fine-tuning | ❌ Not Started | 🟢 Low |
| Distributed Processing | ❌ Not Started | 🟢 Low |

### Success Metrics

**Current State:**
- Test Coverage: Unknown (add pytest-cov)
- Endpoints: 6 REST + MCP
- Tools Available: 1 (google_vision_ocr)
- Models Supported: 0 (OCR only)
- Deployment Regions: 1 (us-central1)

**6-Month Target:**
- Test Coverage: >80%
- Endpoints: 20+ (OCR + LLM + RAG + Agents)
- Tools Available: 10+ (various MCP tools)
- Models Supported: 5+ (multi-provider)
- Deployment Regions: 3+ (multi-region scaling)

### Dependencies & Prerequisites

**For LLM Integration:**
- google-cloud-aiplatform
- google-generativeai
- anthropic (for Claude)
- openai (for GPT-4)
- langchain
- langgraph

**For RAG:**
- pinecone-client or weaviate-client
- sentence-transformers
- PyPDF2 (for chunking)

**For State Store:**
- sqlalchemy
- psycopg2-binary (PostgreSQL)
- alembic (migrations)

**For Observability:**
- python-json-logger
- opentelemetry-api
- opentelemetry-sdk
- langsmith

---

For each phase, see the codebase and docs for detailed implementation and test coverage.
