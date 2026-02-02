# MCP Adapter Implementation Plan

**Project:** Agentic Platform  
**Phase:** 7 - Real Integrations  
**Component:** Model Context Protocol (MCP) Adapter  
**Status:** Planning  
**Date:** 2026-02-01

---

## 1. What is MCP & Why We Need It

### Model Context Protocol (MCP)
- **Purpose:** Standardized protocol for AI models (Claude, etc.) to discover and call tools
- **Use Case:** Allow Claude to invoke your tool registry (OCR, workflow execution, etc.)
- **Benefits:**
  - Turns your tools into a "Claude skill set"
  - Enables complex multi-turn workflows with reasoning
  - Standardized, vendor-neutral approach

### Current State
- Stub `MCPAdapter` exists in `src/agentic_platform/adapters/mcp_adapter.py`
- Already registered in tool registry
- Called by `/run-workflow/` endpoint when adapter=mcp

### Implementation Goal
- Real MCP server implementation
- Proper tool schema conversion
- Error handling and streaming
- Full test coverage

---

## 2. Architecture Overview

### MCP Protocol Flow
```
┌─────────────────────────────────────────────────────────────┐
│ Client (Claude via Anthropic SDK)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP/WebSocket (MCP Protocol)
                 │
┌────────────────▼────────────────────────────────────────────┐
│ MCPAdapter (StdIO or HTTP Server)                           │
│  ├─ Tool Discovery (list_tools)                             │
│  ├─ Tool Execution (call_tool)                              │
│  └─ Error Handling                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (Internal calls)
                 │
┌────────────────▼────────────────────────────────────────────┐
│ ToolRegistry (Your existing tools)                          │
│  ├─ google_vision_ocr                                       │
│  ├─ summarize (example)                                     │
│  └─ ... other tools                                         │
└─────────────────────────────────────────────────────────────┘
```

### File Structure
```
src/agentic_platform/
├── adapters/
│   ├── mcp_adapter.py          # MCP client (calls remote MCP servers)
│   └── mcp_server.py           # NEW: MCP server (serves your tools to Claude)
├── tools/
│   └── tool_registry.py        # Existing tool registry (MCPServer will use this)
└── ...

tests/
├── unit/
│   └── adapters/
│       └── test_mcp_adapter.py           # Unit tests for MCPAdapter
│       └── test_mcp_server.py            # NEW: Tests for MCPServer
└── integration/
    └── test_mcp_e2e.py                   # NEW: E2E test (mock Claude)
```

---

## 3. Step-by-Step Implementation Plan

### **Step 1: Research & Understand MCP Spec** (1-2 hours)

**Goal:** Understand MCP protocol details

**Tasks:**
1. Read [MCP documentation](https://modelcontextprotocol.io/)
2. Review MCP protocol messages:
   - `initialize` - Handshake
   - `list_tools` - Discover available tools
   - `call_tool` - Execute a tool
   - `complete` - LLM completion with tool use
3. Understand tool schema format (JSON Schema)
4. Review existing `MCPAdapter` stub code in your repo

**Deliverable:** Markdown document with protocol summary

---

### **Step 2: Implement MCPServer (Real MCP Server)**

**Goal:** Create an MCP server that serves your tools to Claude

**Location:** `src/agentic_platform/adapters/mcp_server.py`

**Key Components:**

#### 2a. MCPServer Class
```python
class MCPServer:
    """MCP server that exposes your ToolRegistry to Claude/other clients."""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.server = None  # StdIO or HTTP server
    
    def list_tools(self) -> List[MCPTool]:
        """Return available tools in MCP format."""
        # Convert ToolRegistry tools to MCP format
        pass
    
    def call_tool(self, tool_name: str, args: Dict) -> Dict:
        """Execute tool and return result."""
        # Call tool_registry.call() and format response
        pass
    
    def start(self):
        """Start the MCP server (StdIO or HTTP)."""
        pass
```

#### 2b. Tool Schema Conversion
```python
def convert_tool_to_mcp(tool: ToolSpec) -> MCPTool:
    """Convert ToolRegistry tool to MCP tool format.
    
    MCP format:
    {
        "name": "google_vision_ocr",
        "description": "Extract text from images using Google Vision API",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "..."},
                ...
            },
            "required": ["image_path"]
        }
    }
    """
    pass
```

#### 2c. MCP Protocol Handler
```python
def handle_mcp_request(self, request: Dict) -> Dict:
    """Parse MCP request and dispatch to handler.
    
    Handles:
    - {"jsonrpc": "2.0", "method": "list_tools"}
    - {"jsonrpc": "2.0", "method": "call_tool", "params": {...}}
    """
    pass
```

**Implementation Details:**
- Use `anthropic` library's MCP support (or raw protocol)
- Support StdIO transport (Claude subprocess)
- Proper error handling with MCP error format
- Logging for debugging

**Testing:** Unit tests for each method (mocked tool_registry)

---

### **Step 3: Update MCPAdapter (MCP Client)**

**Goal:** Update existing MCPAdapter to actually call an MCP server

**Location:** `src/agentic_platform/adapters/mcp_adapter.py`

**Current Code (Stub):**
```python
class MCPAdapter:
    def call(self, tool_name: str, args: Dict[str, Any]) -> Any:
        raise NotImplementedError("MCP adapter not yet implemented")
```

**New Implementation:**

```python
class MCPAdapter:
    """Calls external MCP servers (e.g., running Claude with MCP)."""
    
    def __init__(self, mcp_server_url: str = None):
        """
        Args:
            mcp_server_url: URL of MCP server (e.g., http://localhost:3000)
                          If None, use local MCPServer with ToolRegistry
        """
        self.mcp_server_url = mcp_server_url or self._start_local_server()
        self.client = MCPClient(self.mcp_server_url)
    
    def call(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Call tool via MCP protocol."""
        # Send call_tool RPC to MCP server
        result = self.client.call_tool(tool_name, args)
        return result
    
    def list_tools(self) -> List[str]:
        """List available tools from MCP server."""
        tools = self.client.list_tools()
        return [t['name'] for t in tools]
    
    def _start_local_server(self):
        """Start local MCPServer if no URL provided."""
        # Useful for local testing
        pass
```

**Key Methods:**
- `call()` - Main entry point (inherited from ToolClient interface)
- `list_tools()` - Discover tools from remote server
- Error handling with retries
- Logging for debugging

---

### **Step 4: Create Tests**

**Goal:** Full test coverage for MCP implementation

#### 4a. Unit Tests: `tests/unit/adapters/test_mcp_server.py`

```python
class TestMCPServer:
    """Test MCPServer tool discovery and execution."""
    
    def test_list_tools_returns_mcp_format(self):
        """MCPServer.list_tools() returns tools in MCP format."""
        pass
    
    def test_tool_schema_conversion(self):
        """Tool registry tools properly converted to MCP schema."""
        pass
    
    def test_call_tool_with_valid_args(self):
        """MCPServer.call_tool() executes tool and returns result."""
        pass
    
    def test_call_tool_with_invalid_args_returns_error(self):
        """Invalid arguments return MCP error format."""
        pass
    
    def test_call_tool_error_handling(self):
        """Tool execution error properly caught and formatted."""
        pass
```

#### 4b. Unit Tests: `tests/unit/adapters/test_mcp_adapter.py`

```python
class TestMCPAdapter:
    """Test MCPAdapter client behavior."""
    
    @patch('mcp.Client')
    def test_call_delegates_to_mcp_client(self, mock_client):
        """MCPAdapter.call() delegates to MCP client."""
        pass
    
    @patch('mcp.Client')
    def test_list_tools_returns_names(self, mock_client):
        """MCPAdapter.list_tools() returns tool names."""
        pass
    
    @patch('mcp.Client')
    def test_error_handling_with_retries(self, mock_client):
        """MCP client errors are handled with retry logic."""
        pass
```

#### 4c. Integration Tests: `tests/integration/test_mcp_e2e.py`

```python
class TestMCPE2E:
    """End-to-end tests with real MCP server and client."""
    
    def test_mcp_server_and_adapter_together(self):
        """Start MCPServer, call via MCPAdapter, verify result."""
        # 1. Start MCPServer with test tool registry
        # 2. Create MCPAdapter pointing to server
        # 3. Call tool via adapter
        # 4. Verify result
        pass
    
    def test_ocr_via_mcp(self):
        """Call OCR tool through MCP server."""
        # Demonstrates real workflow
        pass
    
    def test_multiple_tool_calls_via_mcp(self):
        """Call multiple tools in sequence via MCP."""
        pass
```

---

### **Step 5: Integrate with Workflow Engine**

**Goal:** Use MCPAdapter in workflows

**Changes to `src/agentic_platform/workflow/engine.py`:**

```python
# No changes needed - engine already calls tool_client.call()
# MCPAdapter will work transparently once implemented
```

**Example Workflow:** `workflows/mcp_demo.yaml`

```yaml
nodes:
  - id: start
    type: start
  - id: ocr_step
    type: tool
    tool: google_vision_ocr
  - id: analyze_step
    type: tool
    tool: summarize  # MCP-exposed tool
  - id: end
    type: end

edges:
  - from: start
    to: ocr_step
  - from: ocr_step
    to: analyze_step
  - from: analyze_step
    to: end
```

---

### **Step 6: UI Demo Component**

**Goal:** Test MCP in web UI

**Changes to `ui/src/App.jsx`:**

Add new section:
```jsx
{/* MCP Demo Section */}
<Card sx={{ my: 3 }}>
  <CardContent>
    <Typography variant="h5" fontWeight={600} gutterBottom>MCP Demo</Typography>
    <TextField
      label="Tool Name"
      value={mcpToolName}
      onChange={(e) => setMcpToolName(e.target.value)}
    />
    <TextField
      label="Tool Arguments (JSON)"
      multiline
      rows={4}
      value={mcpArgs}
      onChange={(e) => setMcpArgs(e.target.value)}
    />
    <Button onClick={handleMcpCall}>Call Tool via MCP</Button>
    {mcpResult && (
      <Box sx={{ mt: 3, background: '#f6f8fa', p: 2, borderRadius: 2 }}>
        <pre>{JSON.stringify(mcpResult, null, 2)}</pre>
      </Box>
    )}
  </CardContent>
</Card>
```

**Features:**
- Input tool name and arguments
- Call tool via MCP endpoint
- Display structured result
- Error handling

---

### **Step 7: Documentation**

**Goal:** Document MCP implementation

**Files to Create/Update:**

1. **ADR-010: MCP Server Integration** (`docs/decisions/adr-010-mcp-server.md`)
   - Problem: Need standardized way for Claude to call tools
   - Decision: Implement MCP server + update MCPAdapter
   - Rationale: MCP is becoming standard for AI tool use
   - Trade-offs: Additional dependency, learning curve

2. **Update `docs/api.md`**
   - Add MCP endpoint examples
   - Document tool discovery flow

3. **Update `docs/architecture.md`**
   - Add MCP server architecture
   - Tool schema conversion process

4. **Create `docs/mcp-guide.md`**
   - How to call tools via MCP
   - Example: Using Claude with your tools
   - Troubleshooting guide

---

## 4. Implementation Order (Recommended)

### **Phase 1: Core Implementation** (Day 1-2)
1. ✅ Research MCP spec
2. ✅ Implement MCPServer class
3. ✅ Implement tool schema conversion
4. ✅ Update MCPAdapter to call MCPServer
5. ✅ Add basic logging

### **Phase 2: Testing** (Day 2-3)
6. ✅ Unit tests for MCPServer
7. ✅ Unit tests for MCPAdapter
8. ✅ Integration tests (server + client)
9. ✅ E2E test with real tool execution

### **Phase 3: Integration & Demo** (Day 3-4)
10. ✅ Update workflow engine example
11. ✅ Add UI demo component
12. ✅ Test OCR → MCP workflow
13. ✅ Fix any issues, polish

### **Phase 4: Documentation** (Day 4)
14. ✅ Write ADR-010
15. ✅ Update existing docs
16. ✅ Create MCP guide with examples

---

## 5. Key Technical Decisions

### MCP Transport Layer
**Options:**
- StdIO (Claude runs as subprocess)
- HTTP (Server running on localhost)
- WebSocket (Real-time updates)

**Recommendation:** Start with HTTP for simplicity, mock in tests

### Tool Schema Format
**Approach:**
- Use existing tool schema in `ToolSpec`
- Convert to JSON Schema for MCP
- Validate tool arguments with jsonschema

### Error Handling
**Strategy:**
- Catch all tool execution errors
- Format as MCP error response
- Include stack trace in dev mode, hide in production

### Logging
**Approach:**
- Log all tool calls (tool name, args)
- Log tool results
- Log errors with full context
- Useful for debugging Claude interactions

---

## 6. Expected Outcomes

### After Completion
✅ Claude can discover your tools via MCP  
✅ Claude can call any tool (OCR, summarize, etc.)  
✅ Full error handling and logging  
✅ UI demo for manual testing  
✅ E2E workflow: Extract text (OCR) → Analyze (Claude MCP tool)  
✅ Well-documented architecture  
✅ Production-ready implementation  

### Use Cases Unlocked
- Claude analyzes OCR output
- Multi-step workflows with AI reasoning
- Tool chaining and conditional logic
- Error recovery with Claude assistance

---

## 7. Success Criteria

- [ ] All unit tests pass (MCPServer, MCPAdapter)
- [ ] All integration tests pass
- [ ] E2E test demonstrates OCR → MCP workflow
- [ ] UI demo works and shows results
- [ ] Documentation is complete
- [ ] No debug code or print statements
- [ ] Clean git commits with clear messages
- [ ] Roadmap updated with completion

---

## 8. Common Issues & Solutions

### Issue: Tool schema validation fails
**Solution:** Use jsonschema library to validate before/after conversion

### Issue: MCP client hangs waiting for response
**Solution:** Add timeout with retry logic and clear error message

### Issue: Claude doesn't see your tools
**Solution:** Verify list_tools returns correct MCP format, check schema

### Issue: Tests are flaky
**Solution:** Use proper mocking, avoid real API calls, add deterministic tests

---

## 9. Next Steps After MCP

Once MCP is complete:
1. **Policy Enforcement** - Add tool allowlist
2. **PII Redaction** - Scrub sensitive data
3. **OCR + MCP Demo** - Real-world workflow
4. **Production Deployment** - GKE setup

---

## Summary

This plan takes you from MCP research to a fully-tested, documented implementation that enables Claude to use your tools. Each step builds incrementally, with clear testing at each phase.

**Total Effort:** ~3-4 days of focused development  
**Output:** Production-ready MCP server + adapter  
**Unlocks:** AI-powered workflows with Claude

Ready to start? Let's begin with **Step 1: Research & Planning** → then move to implementation.
