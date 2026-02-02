
etc# Model Context Protocol (MCP) Implementation

The Agentic Platform fully implements the [Model Context Protocol](https://modelcontextprotocol.io) specification, enabling integration with Claude, LLMs, and other MCP-compatible clients.

## Quick Start

### 1. Run the Platform

```bash
# Development
python -m uvicorn src.agentic_platform.api:app --host 0.0.0.0 --port 8080

# Or use Docker
docker build -t agentic-platform .
docker run -p 8080:8080 agentic-platform
```

### 2. Test MCP Endpoints

**List available tools:**
```bash
curl https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/tools
```

**Call a tool:**
```bash
curl -X POST https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request \
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

## Architecture

```
┌──────────────────────────┐
│   MCP Client             │
│ (Claude, LLM, CLI)       │
└───────────┬──────────────┘
            │ HTTP/JSON-RPC
            ▼
┌──────────────────────────────────────┐
│  Agentic Platform API Server         │
├──────────────────────────────────────┤
│  GET  /mcp/tools                     │  List all available tools
│  POST /mcp/request                   │  Call a tool via JSON-RPC 2.0
│  POST /run-ocr/                      │  OCR workflow endpoint
│  POST /run-workflow/                 │  Execute workflows
└──────────────┬───────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
  ┌─────────┐      ┌──────────────┐
  │ MCPServer│      │ Tool Registry│
  │ (JSON-RPC)     │ (Metadata)   │
  └────┬────┘      └──────┬───────┘
       │                  │
       └──────────────────┤
                          ▼
              ┌─────────────────────┐
              │ Available Tools:    │
              │ • google_vision_ocr │
              │ • [Add more here]   │
              └─────────────────────┘
```

## API Reference

### GET /mcp/tools

List all available MCP tools with schemas.

**Response:**
```json
{
  "tools": [
    {
      "name": "google_vision_ocr",
      "description": "Extract text from images using Google Vision API",
      "inputSchema": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Path to image file"
          }
        },
        "required": ["image_path"]
      }
    }
  ]
}
```

### POST /mcp/request

Execute a tool using JSON-RPC 2.0 format.

**Request Body:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "google_vision_ocr",
    "arguments": {
      "image_path": "/sample_data/ocr_sample_plaid.jpg"
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Extracted text from image..."
      }
    ]
  },
  "id": 1
}
```

## Supported Tools

### 1. google_vision_ocr
- **Description:** Extract text from images using Google Vision API
- **Requires:** Google Cloud credentials
- **Input:** `image_path` (string) - path to image file
- **Output:** Extracted text and confidence scores

## Integration Examples

### Using Claude (Coming Soon)
When Claude gains MCP client capabilities, integrate with:
```bash
claude --mcp https://agentic-platform-api-7erqohmwxa-uc.a.run.app
```

### Using Python Client
```python
import requests

response = requests.post(
    'https://agentic-platform-api-7erqohmwxa-uc.a.run.app/mcp/request',
    json={
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': 'google_vision_ocr',
            'arguments': {'image_path': 'image.jpg'}
        },
        'id': 1
    }
)
print(response.json())
```

### Using Node.js
```javascript
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
        arguments: { image_path: 'image.jpg' }
      },
      id: 1
    })
  }
);
const data = await response.json();
console.log(data);
```

## Error Handling

### Invalid Request
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  },
  "id": null
}
```

### Method Not Found
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": 1
}
```

### Invalid Parameters
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params: Missing required argument 'image_path'"
  },
  "id": 1
}
```

## Best Practices

1. **Always validate input** - Check required parameters before sending requests
2. **Handle timeouts** - OCR can take 5-30 seconds depending on image size
3. **Cache results** - Store OCR results to avoid reprocessing
4. **Error recovery** - Implement exponential backoff for retries
5. **Monitor usage** - Log all MCP requests for audit trails

## Testing

Run MCP tests:
```bash
pytest tests/unit/adapters/test_mcp_adapter.py -v
pytest tests/integration/ -k mcp -v
```

## Related Documentation

- [Architecture Overview](./architecture.md)
- [API Reference](./api.md)
- [Tool Registry & Adapters](./adapters.md)
- [Decision: MCP Server Integration](./decisions/adr-010-mcp-server-integration.md)

## Implementation Files

- `src/agentic_platform/adapters/mcp_server.py` - JSON-RPC 2.0 server
- `src/agentic_platform/tools/tool_registry.py` - Tool registration & discovery
- `src/agentic_platform/api.py` - HTTP endpoints (/mcp/tools, /mcp/request)
