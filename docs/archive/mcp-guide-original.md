# MCP Implementation Guide

## Overview

The Model Context Protocol (MCP) is a standardized protocol for AI platforms to interact with tools and services. This guide describes how the Agentic Platform implements MCP, making all registered tools available via a JSON-RPC 2.0 interface.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Integration Guide](#integration-guide)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

## Quick Start

### 1. Start the Platform

```bash
# Install dependencies
pip install -e .

# Start the API server
python -m uvicorn src.agentic_platform.api:app --host localhost --port 8002
```

### 2. List Available Tools

```bash
curl http://localhost:8002/mcp/tools
```

### 3. Call a Tool

```bash
curl -X POST http://localhost:8002/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "/sample_data/ocr_sample_plaid.jpg"}
    },
    "id": 1
  }'
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│           External MCP Client                       │
│   (Claude, MCP CLI, Other Platforms)               │
└────────────────┬────────────────────────────────────┘
                 │
                 │ HTTP/JSON-RPC 2.0
                 ▼
┌─────────────────────────────────────────────────────┐
│         FastAPI HTTP Server (port 8002)             │
│  ┌──────────────────────────────────────────────┐   │
│  │  /mcp/request (POST)                         │   │
│  │  /mcp/tools (GET)                            │   │
│  └──────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         MCPServer (JSON-RPC Handler)                │
│  - Request parsing & validation                     │
│  - Method routing (tools/call, tools/list)          │
│  - Error handling & response formatting             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│            ToolRegistry                             │
│  - Tool discovery                                   │
│  - Tool metadata                                    │
│  - Schema conversion                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│          Available Tools                            │
│  - google_vision_ocr                                │
│  - [Future tools here]                              │
└─────────────────────────────────────────────────────┘
```

### Key Classes

#### MCPServer
Located in `src/agentic_platform/adapters/mcp_server.py`

Implements JSON-RPC 2.0 MCP protocol:
- `handle_request(request)` - Main entry point
- `list_tools()` - Returns available tools
- `call_tool(name, arguments)` - Executes a tool
- Schema conversion and validation

#### MCPAdapter
Located in `src/agentic_platform/adapters/mcp_adapter.py`

HTTP client for calling MCP servers:
- Tool discovery
- Tool execution
- Error handling and retries

#### ToolRegistry
Located in `src/agentic_platform/tools/tool_registry.py`

Central registry for all tools:
- Tool registration
- Tool metadata (name, description, schema)
- Tool instantiation

## API Reference

### GET /mcp/tools

List all available tools with metadata.

**Response:**
```json
{
  "tools": [
    {
      "name": "google_vision_ocr",
      "description": "Extract text from images using Google Cloud Vision API",
      "inputSchema": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Path to the image file"
          }
        },
        "required": ["image_path"]
      }
    }
  ]
}
```

### POST /mcp/request

Execute a tool using JSON-RPC 2.0 MCP protocol.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1",
      "param2": "value2"
    }
  },
  "id": 1
}
```

**Success Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tool_result": "output data"
  },
  "id": 1
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Description of error"
  },
  "id": 1
}
```

**Query Parameters:**
- `method` - MCP method to call
  - `tools/call` - Execute a tool
  - `tools/list` - List tools (use GET /mcp/tools instead)
- `params.name` - Name of the tool to call
- `params.arguments` - Tool arguments (must match inputSchema)

**Response Codes:**
- `200 OK` - Tool executed successfully
- `200 OK` with error object - Tool execution failed (check error.code)
- `400 Bad Request` - Invalid request format
- `500 Internal Server Error` - Server error

## Usage Examples

### Python

```python
import requests
import json

BASE_URL = "http://localhost:8002"

# List tools
response = requests.get(f"{BASE_URL}/mcp/tools")
tools = response.json()["tools"]
print(f"Available tools: {[t['name'] for t in tools]}")

# Call a tool
request = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "google_vision_ocr",
        "arguments": {
            "image_path": "/path/to/image.jpg"
        }
    },
    "id": 1
}

response = requests.post(
    f"{BASE_URL}/mcp/request",
    json=request,
    headers={"Content-Type": "application/json"}
)

result = response.json()
if "result" in result:
    print(f"Tool result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### JavaScript

```javascript
const baseUrl = "http://localhost:8002";

// List tools
async function listTools() {
  const response = await fetch(`${baseUrl}/mcp/tools`);
  const data = await response.json();
  return data.tools;
}

// Call a tool
async function callTool(name, arguments_) {
  const request = {
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
      name: name,
      arguments: arguments_
    },
    id: 1
  };

  const response = await fetch(`${baseUrl}/mcp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });

  return await response.json();
}

// Usage
(async () => {
  const tools = await listTools();
  console.log("Tools:", tools);

  const result = await callTool("google_vision_ocr", {
    image_path: "/sample_data/ocr_sample_plaid.jpg"
  });
  console.log("Result:", result);
})();
```

### cURL

```bash
# List tools
curl http://localhost:8002/mcp/tools

# Call tool with pretty-printed output
curl -X POST http://localhost:8002/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "google_vision_ocr",
      "arguments": {"image_path": "/sample_data/ocr_sample_plaid.jpg"}
    },
    "id": 1
  }' | jq .
```

## Integration Guide

### Adding New Tools to MCP

1. **Create a Tool Class**

```python
from src.agentic_platform.agents.base import Tool

class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what the tool does",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter"
                    }
                },
                "required": ["param1"]
            }
        )
    
    async def run(self, arguments):
        # Tool implementation
        result = self.do_something(arguments.get("param1"))
        return {"result": result}
```

2. **Register Tool**

```python
from src.agentic_platform.tools.tool_registry import ToolRegistry

registry = ToolRegistry()
registry.register(MyTool)
```

3. **Tool is Automatically Available via MCP**

```bash
curl http://localhost:8002/mcp/tools
# Now includes "my_tool" in the list
```

### Integrating with External Platforms

#### Claude Desktop
1. Add MCP configuration to Claude's `claude_desktop_config.json`
2. Specify the server URL: `http://localhost:8002/mcp/request`
3. Claude can now discover and use platform tools

#### Custom MCP Clients
1. Connect to `/mcp/tools` to discover available tools
2. Build requests to `/mcp/request` in JSON-RPC 2.0 format
3. Handle responses and errors appropriately

## Error Handling

### JSON-RPC Error Codes

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON was received |
| -32600 | Invalid Request | The JSON sent is not a valid Request object |
| -32601 | Method not found | The method does not exist / is not available |
| -32602 | Invalid params | Invalid method parameter(s) |
| -32603 | Internal error | Internal JSON-RPC error |

### Example Error Responses

**Invalid Tool Name:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Tool 'unknown_tool' not found in registry"
  },
  "id": 1
}
```

**Invalid Arguments:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Missing required parameter: image_path"
  },
  "id": 1
}
```

**Tool Execution Error:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": "Tool execution failed: Failed to read file /nonexistent/image.jpg"
  },
  "id": 1
}
```

## Best Practices

### 1. Request Validation
- Always validate JSON-RPC 2.0 format
- Check that required parameters are present
- Validate argument types match schema

### 2. Error Handling
- Handle connection timeouts gracefully
- Retry failed requests with exponential backoff
- Log error details for debugging

### 3. Tool Development
- Provide clear, actionable descriptions
- Define comprehensive inputSchema
- Return consistent result structures
- Document expected errors

### 4. Performance
- Cache tool metadata after first discovery
- Implement connection pooling for multiple requests
- Use async/await for non-blocking calls

### 5. Security
- Validate input arguments before passing to tools
- Implement rate limiting for tool calls
- Log all tool executions for audit trails
- Use HTTPS in production

## Testing

### Unit Tests
```bash
pytest tests/unit/adapters/test_mcp_server.py
pytest tests/unit/adapters/test_mcp_adapter.py
```

### Integration Tests
```bash
pytest tests/integration/test_mcp_e2e.py
```

### Manual Testing
Use the React UI at `http://localhost:5173` or cURL commands in the examples.

## Troubleshooting

### Tools Not Appearing
- Check that tools are registered in ToolRegistry
- Verify GET /mcp/tools returns expected list
- Check application logs for registration errors

### Tool Calls Failing
- Verify tool name is correct (check GET /mcp/tools)
- Validate arguments match inputSchema
- Check application logs for execution errors
- Ensure required files/resources exist

### Connection Issues
- Verify API server is running on port 8002
- Check firewall rules allow access
- Try cURL to diagnose network issues

## References

- [MCP Specification](https://modelcontextprotocol.io)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [API Documentation](./api.md)
- [Architecture Documentation](./architecture.md)
- [ADR-010: MCP Server Integration](./decisions/adr-010-mcp-server-integration.md)
