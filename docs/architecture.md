## Architecture Overview

This document describes the architecture, interfaces, and extension points of the Agentic Platform with current implementation status.

## High-Level Architecture
```
┌─────────────────────────────────────────────┐
│  React UI (Material-UI)                     │
│  - OCR Demo, MCP Tester, Workflow Runner    │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────┐
│  FastAPI Backend (Port 8003)                │
│  ├─ /run-ocr/          → GoogleVisionOCR    │
│  ├─ /run-workflow/     → Adapter selection  │
│  ├─ /mcp/tools         → Tool discovery     │
│  └─ /mcp/request       → MCP JSON-RPC 2.0   │
└──────────────────┬──────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Workflow   │ │ Tool       │ │ Audit      │
│ Engine     │ │ Registry   │ │ Log        │
│ (YAML DAG) │ │ (Plugin)   │ │ (Events)   │
└────────────┘ └────────────┘ └────────────┘
    │              │
    └──────────────┼──────────────────┐
                   │                  │
           ┌───────▼──────────┐    ┌──▼──────────────┐
           │ Adapters         │    │ External APIs   │
           ├─ MCPAdapter ✅   │    ├─ Google Vision  │
           ├─ LangGraphAdpter │    ├─ MCP Clients    │
           │  🔄 (Phase 9)    │    └─────────────────┘
           └──────────────────┘
```

## Component Status

### ✅ Implemented Components
- **UI:** React 18 + Material-UI (OCR, MCP Tester, Workflow Runner)
- **API:** FastAPI with 4 core endpoints (/run-ocr, /run-workflow, /mcp/tools, /mcp/request)
- **Core:** Type definitions, IDs (JobId, CorrelationId), error handling
- **Audit:** In-memory immutable event log with correlation tracking
- **Tools:** 
  - ToolRegistry with plugin system ✅
  - GoogleVisionOCR adapter ✅
  - MCP Server with JSON-RPC 2.0 ✅
- **Workflow:** 
  - YAML parser with DAG validation ✅
  - Engine with branching, retry, state management ✅
  - In-memory execution ✅
- **Adapters:** 
  - MCPAdapter (HTTP client) ✅ 
  - GoogleVisionOCR ✅
  - LangGraphAdapter (stub - Phase 9) 🔄

### 🔄 In Development (Phase 9)
- **LangGraphAdapter:** Real implementation (state graph, LLM integration, tool binding)
- **LLM Providers:** Factory built, not yet active (Anthropic, OpenAI, Google, Mock)

### ❌ Not Yet Implemented
- **Data Persistence:** PostgreSQL (Phase 10)
- **Authentication:** JWT, OAuth2 (Phase 10)
- **Authorization:** RBAC (Phase 10)
- **RAG System:** Vector DB, embeddings (Phase 12)
- **Real-time Streaming:** SSE (Phase 12)
- **Observability:** Prometheus, ELK, distributed tracing (Phase 11)
- **Infrastructure as Code:** Terraform, Helm (Phase 10)

## Key Interfaces (Ports)
```python
class ToolClient:
    def call(self, tool_name: str, args: Dict) -> Dict:
        """Execute tool and return result"""
        pass
    
    def list_tools(self) -> List[Dict]:
        """List available tools with schemas"""
        pass

class ArtifactStore:
    def put(self, job_id: str, artifact: Dict) -> str:
        """Store artifact, return reference"""
        pass
    
    def get(self, ref: str) -> Dict:
        """Retrieve artifact by reference"""
        pass

class AuditLog:
    def emit(self, event: AuditEvent) -> None:
        """Record immutable event"""
        pass
    
    def get_events(self, job_id: str) -> List[AuditEvent]:
        """Retrieve events for job"""
        pass
```

## Design Principles
- **Adapter Pattern:** All external integrations are swappable
- **Testability:** High test coverage (57+ tests), mockable interfaces
- **Separation of Concerns:** Core logic isolated from integrations
- **Configurability:** Runtime adapter selection, dependency injection
- **Incremental:** Vertical slice development with comprehensive testing

## Extension Points

1. **New Adapters:** Add to `src/agentic_platform/adapters/`
2. **New Tools:** Register in ToolRegistry
3. **New Workflow Nodes:** Extend WorkflowEngine
4. **Audit Hooks:** Extend AuditLog implementation
5. **Persistence:** Implement ArtifactStore interface

## Deployment Architecture

### Current (Phase 8)
- Single container (FastAPI + React)
- Google Cloud Run
- In-memory state
- Application Default Credentials (ADC) for Google APIs

### Planned (Phase 10+)
- Frontend/Backend separation (optional)
- Kubernetes-ready Helm charts
- PostgreSQL backend
- Secrets management (GCP Secret Manager)
- Multi-region deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud setup details.
