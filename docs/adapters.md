# Adapter Integrations

This document describes the adapter pattern and current implementation status for the Agentic Platform.

## Adapter Pattern
- All external systems (MCP, LangGraph, n8n, S3, DB, SaaS) are integrated via adapters in `src/agentic_platform/adapters/`.
- Adapters expose a common interface: `call(tool_name, args) -> result`.
- Adapters can be swapped for tests, simulation, or real backends.
- **Status:** Testable pattern established; extensible for new adapters.

## Current Adapters

### ✅ MCP Adapter (IMPLEMENTED)
- **File:** `src/agentic_platform/adapters/mcp_adapter.py`
- **Status:** Production-ready ✅
- **Capabilities:**
  - HTTP JSON-RPC 2.0 client for MCP servers
  - Tool discovery (`list_tools`)
  - Tool execution (`call_tool`)
  - Error handling with proper logging
  - Timeout handling (30s default)
- **Used in:** CLI, API `/run-workflow/` with `adapter=mcp`, tests
- **Tests:** 22+ unit tests, 13+ E2E tests

### ✅ GoogleVisionOCR Adapter (IMPLEMENTED)
- **File:** `src/agentic_platform/adapters/ocr_adapter.py`
- **Status:** Production-ready ✅
- **Capabilities:**
  - Image OCR via Google Vision API
  - Confidence scoring (simple, complex, hard-to-read)
  - Layout complexity detection
  - Application Default Credentials (ADC) auth
- **Used in:** `/run-ocr/` endpoint, workflows, MCP tools
- **Tests:** 14+ unit tests with confidence scoring validation

### 🔄 LangGraph Adapter (STUB - PHASE 9)
- **File:** `src/agentic_platform/adapters/langgraph_adapter.py`
- **Status:** Stub only - returns simulated responses 🔄
- **Current State:**
  - No real LangGraph implementation
  - No graph execution or state management
  - No LLM integration (factory built, not used)
  - Mock responses for testing purposes
- **Dependencies Installed:** `langgraph`, `langchain`, LLM providers configured
- **Phase 9 Tasks:**
  - StateGraph definition with agent/tool/decision nodes
  - Real LLM integration (Anthropic/OpenAI/Google)
  - Tool binding to MCP tools
  - Streaming support for token-level responses
  - Comprehensive test coverage (25+ tests)
- **Used in:** Workflow engine when `adapter=langgraph` selected
- **Target Completion:** Feb 28, 2026

### ❌ Planned Adapters (Future Phases)
- **n8nAdapter** - n8n workflow orchestration (Phase 12+)
- **S3ArtifactStore** - AWS S3 artifact persistence (Phase 10)
- **DBArtifactStore** - PostgreSQL artifact persistence (Phase 10)
- **PostgreSQLStateStore** - Conversation history (Phase 10)

## Adapter Selection (Runtime)

### Via API
```bash
curl -X POST http://localhost:8003/run-workflow/ \
  -F "workflow=@workflow.yaml" \
  -F "input_artifact=@input.json" \
  -F "adapter=mcp"  # or "langgraph"
```

### Via CLI
```bash
python -m src.agentic_platform.cli \
  --workflow workflow.yaml \
  --input input.json \
  --adapter mcp  # or "langgraph"
```

## Testing Adapters
- See `tests/unit/adapters/test_mcp_adapter.py` - MCP HTTP client tests
- See `tests/unit/adapters/test_langgraph_adapter.py` - LangGraph stub tests
- See `tests/integration/test_mcp_e2e.py` - End-to-end MCP workflow tests
- All adapters use dependency injection for swappable implementations

## Adding New Adapters

1. **Create adapter module:** `src/agentic_platform/adapters/my_adapter.py`
2. **Implement interface:**
   ```python
   class MyAdapter:
       def __init__(self, config=None):
           self.config = config or {}
       
       def call(self, tool_name: str, args: Dict) -> Dict:
           """Execute tool and return result"""
           pass
       
       def list_tools(self) -> List[Dict]:
           """List available tools"""
           pass
   ```
3. **Add unit tests:** `tests/unit/adapters/test_my_adapter.py`
4. **Add to adapter factory:** `src/agentic_platform/api.py`
5. **Update documentation**
