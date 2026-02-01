# ADR-010: MCP Server Integration

**Date:** February 2025  
**Status:** Accepted  
**Context:** The platform needs to standardize tool access via the Model Context Protocol (MCP) to enable interoperability with MCP-compatible clients and tools.

## Problem Statement

Tool access was previously limited to direct adapter implementations, making it difficult to:
1. Integrate with MCP-compliant clients (Claude, other AI platforms)
2. Support dynamic tool registration and discovery
3. Provide a standardized interface for tool execution

## Decision

Implement a complete MCP server using JSON-RPC 2.0 protocol that:

1. **MCPServer class** - HTTP-based MCP protocol handler
   - Handles JSON-RPC 2.0 requests/responses
   - Implements `tools/list` method for tool discovery
   - Implements `tools/call` method for tool execution
   - Supports schema conversion between tool definitions and MCP format
   - Proper error handling with MCP-compliant error codes

2. **FastAPI HTTP endpoints** - Public MCP interface
   - `POST /mcp/request` - Handle JSON-RPC 2.0 MCP requests
   - `GET /mcp/tools` - List available tools in simplified format

3. **Integration with ToolRegistry** - Centralized tool management
   - ToolRegistry as single source of truth for available tools
   - Dynamic tool metadata (name, description, inputSchema)
   - Lazy tool instantiation and execution

## Implementation Details

### MCPServer Class Architecture

```python
class MCPServer:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.protocol_version = "2024-11-05"
    
    async def handle_request(self, request: Dict) -> Dict:
        """Main entry point for JSON-RPC 2.0 requests"""
        # Validates JSON-RPC format
        # Routes to appropriate handler (initialize, tools/list, tools/call)
        # Returns JSON-RPC response
    
    async def list_tools(self) -> List[MCPTool]:
        """Returns available tools in MCP format"""
        # Fetches all tools from registry
        # Converts to MCP tool schema
        # Includes inputSchema for parameter validation
    
    async def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Executes a tool with provided arguments"""
        # Validates tool exists
        # Executes tool.run(arguments)
        # Captures result or error
        # Returns in MCP format
```

### MCP Protocol Support

- **JSON-RPC 2.0 Compliance**
  - Request/response message format
  - Error codes: -32700, -32600, -32601, -32602, -32603
  - Request ID tracking

- **Protocol Methods**
  - `initialize` - Protocol negotiation
  - `tools/list` - Tool discovery
  - `tools/call` - Tool execution

### FastAPI Integration

```python
@app.post("/mcp/request")
async def mcp_request(request: dict):
    """Handle MCP JSON-RPC 2.0 requests"""
    response = await mcp_server.handle_request(request)
    return response

@app.get("/mcp/tools")
async def mcp_tools():
    """List available tools"""
    tools = await mcp_server.list_tools()
    return {"tools": tools}
```

## API Examples

### List Tools

```bash
curl http://localhost:8002/mcp/tools
```

Response:
```json
{
  "tools": [
    {
      "name": "google_vision_ocr",
      "description": "Extract text from images using Google Cloud Vision API",
      "inputSchema": {
        "type": "object",
        "properties": {
          "image_path": {"type": "string"},
          "credentials_json": {"type": "string", "default": null}
        },
        "required": ["image_path"]
      }
    }
  ]
}
```

### Call Tool

```bash
curl -X POST http://localhost:8002/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "/path/to/image.jpg"}
    },
    "id": 1
  }'
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "text": "Extracted text content",
    "confidence": 0.95,
    "formatted_text_lines": ["Line 1", "Line 2"]
  },
  "id": 1
}
```

## Benefits

1. **Interoperability** - MCP-compliant clients can now use platform tools
2. **Standardization** - JSON-RPC 2.0 protocol compliance
3. **Tool Discovery** - Centralized tool registry and metadata
4. **Error Handling** - Standard MCP error codes and messages
5. **Scalability** - Multiple tools can be registered and discovered dynamically

## Testing

- **Unit Tests** - MCPServer protocol handling, schema conversion
  - 22 test cases covering all methods and error scenarios
  - Schema validation and error code generation
  
- **Integration Tests** - End-to-end MCP workflow
  - 13 test cases covering tool calling via MCP
  - OCR tool execution through MCP endpoints
  - Error handling and edge cases

- **UI Demo** - React component for tool testing
  - Tool discovery and selection
  - JSON argument input with validation
  - Result display with formatting

## Files Changed

- **New:** `src/agentic_platform/adapters/mcp_server.py` (425 lines)
- **Updated:** `src/agentic_platform/api.py` (added `/mcp/request` and `/mcp/tools` endpoints)
- **Updated:** `ui/src/App.jsx` (added MCP Demo section with tool tester)
- **New:** Complete test coverage (57 tests total)

## Rollout Plan

1. ✅ Implement MCPServer and MCPAdapter
2. ✅ Add FastAPI endpoints
3. ✅ Comprehensive unit + integration tests
4. ✅ React UI demo component
5. ✅ Documentation and guides
6. → Ready for production deployment

## Future Enhancements

1. MCP client mode - Call external MCP servers
2. Tool authentication - API key management for tools
3. Rate limiting - Per-tool call limits
4. Usage analytics - Track tool usage patterns
5. Tool versioning - Support multiple tool versions

## References

- [MCP Specification](https://modelcontextprotocol.io)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [ADR-008: Artifact Store Integration](./adr-008-artifact-store-integration.md)
- [ADR-003: Adapter Pattern](./adr-003-adapter-pattern.md)
