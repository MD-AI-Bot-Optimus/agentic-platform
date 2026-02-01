# MCP Research & Specification Summary

**Date:** February 1, 2026  
**Status:** Research Complete  
**Task:** Understanding MCP protocol and current implementation gap

---

## 1. What is MCP (Model Context Protocol)?

### Core Concept
**MCP is like a "USB-C port for AI applications"** — a standardized protocol for connecting AI systems (Claude, ChatGPT) to external tools, data sources, and workflows.

### Key Analogy
- **Traditional:** Each AI app builds custom integrations
- **With MCP:** Standardized protocol enables easy plug-and-play connections

### Why It Matters
- **Developers:** Faster integration with AI apps, less custom code
- **AI Apps:** Access to ecosystem of tools and data sources
- **End Users:** More capable AI that can access their data and tools

---

## 2. MCP Architecture Layers

### Layer 1: Data Layer (JSON-RPC 2.0 Protocol)
**What:** Defines messages, semantics, and primitives for client-server communication

**Key Components:**
- **Lifecycle Management:** Initialization, capability negotiation, connection termination
- **Server Features:** What server provides (tools, resources, prompts)
- **Client Features:** What client can offer (sampling, elicitation, logging)
- **Notifications:** Real-time updates when state changes

**Message Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize|tools/list|tools/call|...",
  "params": {...}
}
```

### Layer 2: Transport Layer (How messages move)
**What:** Communication channels between clients and servers

**Two Transport Options:**

1. **StdIO Transport** (Local)
   - Standard input/output streams
   - Direct process communication
   - Single client per server
   - Optimal performance
   - Used by: Claude Desktop with local servers

2. **Streamable HTTP Transport** (Remote)
   - HTTP POST for client→server requests
   - Server-Sent Events (SSE) for streaming responses
   - Multiple clients per server
   - Standard HTTP auth (bearer tokens, API keys, OAuth)
   - Used by: Remote servers (e.g., Sentry)

---

## 3. MCP Primitives (What Servers Can Expose)

### Server Primitives (What Server Provides)

#### **Tools** (Most relevant for your use case)
- **Purpose:** Executable functions AI can invoke
- **Examples:** File operations, API calls, database queries, OCR
- **Your Tools:** `google_vision_ocr`, `summarize`, `translate`, etc.

#### **Resources** 
- **Purpose:** Context data sources
- **Examples:** File contents, database records, API responses

#### **Prompts**
- **Purpose:** Reusable interaction templates
- **Examples:** System prompts, few-shot examples

### Client Primitives (What Client Offers to Server)

#### **Sampling**
- Server requests LLM completions from client's AI app
- Useful: Server wants model access without embedding SDK

#### **Elicitation**
- Server requests user input/confirmation
- Useful: Interactive workflows

#### **Logging**
- Server sends logs to client for monitoring/debugging

---

## 4. MCP Protocol Flow (Detailed)

### **Phase 1: Initialization (Lifecycle Management)**

**Purpose:** Handshake, version negotiation, capability exchange

**Client Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
```

**Server Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {}
    },
    "serverInfo": {
      "name": "agentic-platform",
      "version": "1.0.0"
    }
  }
}
```

**Key Checks:**
1. Protocol version compatibility (must match)
2. Capability negotiation (what each side supports)
3. Identify client & server for debugging

**After Success:**
Client sends notification:
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

---

### **Phase 2: Tool Discovery (Primitives)**

**Purpose:** Client learns what tools server provides

**Client Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**Server Response (Your Implementation Will Return This):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "google_vision_ocr",
        "description": "Extract text from images using Google Vision API",
        "inputSchema": {
          "type": "object",
          "properties": {
            "image_path": {
              "type": "string",
              "description": "Path to the image file to OCR"
            },
            "credentials_json": {
              "type": "string",
              "description": "Path to Google credentials JSON file",
              "default": null
            }
          },
          "required": ["image_path"]
        }
      },
      {
        "name": "summarize",
        "description": "Summarize text using Claude",
        "inputSchema": {
          "type": "object",
          "properties": {
            "text": {"type": "string", "description": "Text to summarize"},
            "max_length": {"type": "integer", "description": "Maximum length of summary"}
          },
          "required": ["text"]
        }
      }
    ]
  }
}
```

**Key Fields:**
- `name` - Unique tool identifier (used in tool/call)
- `description` - What the tool does
- `inputSchema` - JSON Schema for input validation

---

### **Phase 3: Tool Execution (Primitives)**

**Purpose:** Claude calls a tool, server executes and returns result

**Client Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "google_vision_ocr",
    "arguments": {
      "image_path": "/path/to/image.jpg"
    }
  }
}
```

**Server Response (Success):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "OCR extracted text:\n\nThe quick brown fox...\n\nConfidence: 0.95"
      }
    ]
  }
}
```

**Server Response (Error):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "details": "File not found: /path/to/image.jpg"
    }
  }
}
```

**Key Points:**
- `content` is an array (supports multiple types: text, image, resource)
- All errors must follow JSON-RPC error format
- Tool name must match exactly from discovery

---

### **Phase 4: Real-Time Updates (Notifications)**

**Purpose:** Server tells client when tool list changes

**Server Notification (No Response Expected):**
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

**Client Response:** Re-fetches tools/list to get updated list

**Why Important:**
- Tools may appear/disappear based on permissions, external state
- Keeps client's tool registry current
- Only sent if server declared `"listChanged": true` in initialization

---

## 5. Current State: Your Implementation

### **Current Files**

#### `src/agentic_platform/adapters/mcp_adapter.py` (Stub)
```python
class MCPAdapter:
    def __init__(self, config=None):
        self.config = config or {}

    def call(self, tool_name, args):
        # Simulates MCP call, returns canned response
        return {
            "tool": tool_name,
            "args": args,
            "result": f"MCP simulated response for {tool_name}",
            "status": "success"
        }
```

**Status:** ❌ **Stub only**
- Does NOT implement MCP protocol
- Returns mock response
- Not connected to real MCP server

#### `src/agentic_platform/tools/tool_registry.py` (Existing)
```python
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._register_builtin_tools()

    def register_tool(self, name: str, schema: Dict[str, Any], handler: Callable):
        self._tools[name] = ToolSpec(name, schema, handler)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def call(self, name: str, args: Dict[str, Any]) -> Any:
        # Validates args with JSON schema
        # Calls tool handler
        ...
```

**Status:** ✅ **Ready to use**
- Already has `google_vision_ocr` registered
- Has JSON schema validation
- Has tool execution with error handling

---

## 6. Implementation Gap Analysis

### What's Missing (MCPServer)
Your tools exist in `ToolRegistry`, but they're NOT exposed via MCP protocol.

**Gap: Need MCPServer Implementation**

```
┌──────────────────────────────────────────────────┐
│ Claude (MCP Client)                              │
└──────────────────────┬───────────────────────────┘
                       │
                       │ JSON-RPC 2.0 Messages
                       │ (missing this layer)
                       │
┌──────────────────────▼───────────────────────────┐
│ MCPServer (TO BE BUILT)                          │
│  ├─ Receive initialize request                   │
│  ├─ Receive tools/list request                   │
│  ├─ Receive tools/call request                   │
│  └─ Send JSON-RPC responses in MCP format        │
└──────────────────────┬───────────────────────────┘
                       │
                       │ Python method calls
                       │
┌──────────────────────▼───────────────────────────┐
│ ToolRegistry (ALREADY EXISTS ✅)                  │
│  ├─ google_vision_ocr                            │
│  ├─ Other tools...                               │
│  └─ Execution with schema validation             │
└──────────────────────────────────────────────────┘
```

---

## 7. Key Technical Decisions for Implementation

### Decision 1: Transport Layer
**Options:**
- A. StdIO (Claude Desktop runs server as subprocess)
- B. HTTP (Server on localhost, Claude connects via HTTP)

**Recommendation:** **HTTP** for this project
- Easier testing and debugging
- Works with our FastAPI backend
- Can support multiple clients
- Future: Support both for flexibility

---

### Decision 2: MCPServer Architecture
**Two Approaches:**

#### Approach A: Standalone MCPServer Class
```python
class MCPServer:
    def __init__(self, tool_registry, host='localhost', port=3000):
        self.registry = tool_registry
        self.host = host
        self.port = port
    
    def start(self):
        # Run HTTP server, handle JSON-RPC messages
        pass
```

**Pros:** Clear separation, reusable  
**Cons:** Extra service to manage

#### Approach B: Integrated with FastAPI
```python
# In api.py
@app.post("/mcp/initialize")
async def mcp_initialize(request):
    # Handle MCP initialize request
    pass

@app.post("/mcp/tools/list")
async def mcp_tools_list():
    # Handle tools/list request
    pass

@app.post("/mcp/tools/call")
async def mcp_tools_call(request):
    # Handle tools/call request
    pass
```

**Pros:** Single service, integrated with FastAPI  
**Cons:** Mixes concerns

**Recommendation:** **Approach B (Integrated)**
- Simpler deployment
- Aligns with existing `/run-workflow/` pattern
- Can evolve to separate server later

---

### Decision 3: MCPAdapter Update
**Current state:** Returns mock response  
**New behavior:** Make real HTTP calls to MCPServer (or another MCP server)

```python
class MCPAdapter:
    def __init__(self, mcp_server_url="http://localhost:8002"):
        self.mcp_server_url = mcp_server_url
    
    def call(self, tool_name, args):
        # Make HTTP call to MCPServer's tools/call endpoint
        response = requests.post(
            f"{self.mcp_server_url}/mcp/tools/call",
            json={"name": tool_name, "arguments": args}
        )
        # Parse MCP response and return result
        return response.json()["result"]["content"][0]["text"]
```

---

## 8. Tool Schema Conversion Example

### Your Current Schema (ToolRegistry)
```python
ocr_schema = {
    "type": "object",
    "properties": {
        "image_path": {"type": "string", "description": "Path to image"},
        "credentials_json": {"type": "string", "default": None}
    },
    "required": ["image_path"]
}
```

### MCP Format (Same! JSON Schema standard)
```json
{
  "type": "object",
  "properties": {
    "image_path": {"type": "string", "description": "Path to image"},
    "credentials_json": {"type": "string", "default": null}
  },
  "required": ["image_path"]
}
```

**Good News:** Your schemas are already MCP-compatible! Just need to expose them.

---

## 9. Error Handling Strategy

### JSON-RPC Error Format (Required for MCP)
```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "details": "Tool execution failed: <error message>",
      "stack_trace": "... (in dev mode only)"
    }
  }
}
```

### Error Codes
- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

---

## 10. Logging & Debugging Strategy

### MCP Debug Points
1. **Initialization:** Log capability negotiation
2. **Tool Discovery:** Log tools/list responses
3. **Tool Execution:** Log tool_name, args, result, timing
4. **Errors:** Log full stack trace in dev mode

### Recommended Logging
```python
import logging
logger = logging.getLogger("mcp_server")

# In tools/call handler
logger.info(f"Calling tool: {tool_name} with args: {args}")
try:
    result = registry.call(tool_name, args)
    logger.info(f"Tool success: {tool_name}, result length: {len(str(result))}")
except Exception as e:
    logger.error(f"Tool error: {tool_name}", exc_info=True)
```

---

## 11. Testing Strategy for MCP

### Unit Tests
```python
# Test MCPServer methods in isolation
def test_mcp_list_tools_returns_correct_format():
    # Verify response has tools array with name/description/inputSchema

def test_mcp_tool_schema_conversion():
    # Verify ToolRegistry schema → MCP format works

def test_mcp_call_tool_with_valid_args():
    # Mock tool_registry, call tool, verify response

def test_mcp_call_tool_returns_json_rpc_error_format():
    # Invalid args should return proper error
```

### Integration Tests
```python
# Test MCPServer + MCPAdapter together
def test_mcp_end_to_end():
    # Start MCPServer
    # Create MCPAdapter pointing to it
    # Call tool via adapter
    # Verify result
```

### E2E Tests
```python
# Test with real workflow
def test_ocr_via_mcp():
    # Upload image → /run-ocr/ (uses MCPAdapter)
    # Verify text extracted via MCP pipeline
```

---

## 12. Implementation Checklist

### Phase 1: MCPServer Implementation
- [ ] Create `src/agentic_platform/adapters/mcp_server.py`
- [ ] Implement `MCPServer.handle_initialize()`
- [ ] Implement `MCPServer.handle_tools_list()`
- [ ] Implement `MCPServer.handle_tools_call()`
- [ ] Add JSON-RPC response formatting
- [ ] Add error handling with proper error codes
- [ ] Add logging for debugging

### Phase 2: FastAPI Integration
- [ ] Add `/mcp/initialize` endpoint
- [ ] Add `/mcp/tools/list` endpoint
- [ ] Add `/mcp/tools/call` endpoint
- [ ] Wire up ToolRegistry
- [ ] Add request validation

### Phase 3: MCPAdapter Update
- [ ] Update `MCPAdapter.call()` to use HTTP
- [ ] Add `MCPAdapter.list_tools()`
- [ ] Add error handling with retries
- [ ] Add timeout handling

### Phase 4: Testing
- [ ] Unit tests for MCPServer
- [ ] Unit tests for MCPAdapter
- [ ] Integration tests
- [ ] E2E tests with OCR

### Phase 5: Documentation
- [ ] ADR-010: MCP Server Decision
- [ ] Update api.md with MCP endpoints
- [ ] Update architecture.md
- [ ] Create mcp-guide.md with examples

---

## 13. References

- **MCP Official Docs:** https://modelcontextprotocol.io/
- **MCP Architecture:** https://modelcontextprotocol.io/docs/learn/architecture
- **JSON-RPC 2.0:** https://www.jsonrpc.org/
- **JSON Schema:** https://json-schema.org/

---

## Summary

### What We Learned
1. **MCP is JSON-RPC 2.0** over StdIO or HTTP
2. **Three core phases:** Initialize → List Tools → Call Tool
3. **Your ToolRegistry is already MCP-compatible**
4. **Gap:** Need MCPServer to translate MCP protocol → ToolRegistry calls
5. **Strategy:** Integrate with existing FastAPI (3 new endpoints)

### What Needs Building
1. **MCPServer:** Handles JSON-RPC messages, calls ToolRegistry
2. **FastAPI Integration:** 3 new endpoints + JSON-RPC response formatter
3. **MCPAdapter Update:** Make real HTTP calls instead of mock responses
4. **Tests:** Full unit/integration/E2E coverage

### Ready to Build?
Yes! We have all the information needed. Proceeding to **Step 2: Implement MCPServer**.

