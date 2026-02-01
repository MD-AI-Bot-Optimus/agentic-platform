"""
End-to-end integration tests for MCP.

Tests the complete MCP flow:
1. MCPServer starts (via FastAPI)
2. MCPAdapter connects and initializes
3. Discovers tools
4. Calls tools
5. Verifies results

Tests both local server and real tool execution.
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from fastapi.testclient import TestClient
from agentic_platform.api import app, mcp_server, tool_registry
from agentic_platform.adapters.mcp_adapter import MCPAdapter
from agentic_platform.tools.tool_registry import ToolRegistry, ToolSpec


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestMCPE2E:
    """End-to-end MCP tests."""

    def test_mcp_request_endpoint_exists(self, client):
        """MCP request endpoint is available."""
        response = client.post("/mcp/request", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        })
        assert response.status_code == 200

    def test_mcp_tools_endpoint_exists(self, client):
        """MCP tools listing endpoint is available."""
        response = client.get("/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data

    def test_initialize_handshake(self, client):
        """Client can initialize with server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        response = client.post("/mcp/request", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["result"]["protocolVersion"] == "2025-06-18"
        assert "tools" in data["result"]["capabilities"]

    def test_tools_list_via_endpoint(self, client):
        """List tools via HTTP endpoint."""
        response = client.get("/mcp/tools")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["tools"], list)
        # Should have at least OCR tool
        tool_names = [t["name"] for t in data["tools"]]
        assert "google_vision_ocr" in tool_names

    def test_tools_list_via_mcp_protocol(self, client):
        """List tools via MCP protocol."""
        # Initialize first
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        init_response = client.post("/mcp/request", json=init_request)
        assert init_response.status_code == 200

        # List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        list_response = client.post("/mcp/request", json=list_request)

        assert list_response.status_code == 200
        data = list_response.json()
        assert "result" in data
        assert "tools" in data["result"]
        tools = data["result"]["tools"]
        assert len(tools) > 0
        assert tools[0]["name"] == "google_vision_ocr"

    def test_tool_call_error_handling(self, client):
        """MCP properly handles tool execution errors."""
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        client.post("/mcp/request", json=init_request)

        # Try to call with non-existent file
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "google_vision_ocr",
                "arguments": {"image_path": "/nonexistent/path/to/image.jpg"}
            }
        }
        response = client.post("/mcp/request", json=call_request)

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32603  # Internal error
        assert "No such file" in data["error"]["message"]

    def test_mcp_adapter_local_mode(self, client):
        """MCPAdapter can call local MCP server."""
        # Initialize via MCP protocol first
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "adapter-test", "version": "1.0"}
            }
        }
        init_response = client.post("/mcp/request", json=init_request)
        assert init_response.status_code == 200

        # Create adapter pointing to test server
        adapter = MCPAdapter("http://testserver/")  # TestClient base URL
        adapter.client.base_url = "http://testserver"  # Use TestClient

        # Mock requests to use TestClient
        with patch("agentic_platform.adapters.mcp_adapter.requests.post") as mock_post:
            def post_handler(url, **kwargs):
                # Route to TestClient
                path = url.replace("http://testserver/mcp/request", "")
                response = client.post("/mcp/request", json=kwargs.get("json"))
                mock_response = Mock()
                mock_response.json.return_value = response.json()
                mock_response.raise_for_status.return_value = None
                return mock_response

            mock_post.side_effect = post_handler

            # List tools
            tools = adapter.list_tools()
            assert "google_vision_ocr" in tools

    def test_multiple_sequential_calls(self, client):
        """Multiple tool calls work correctly."""
        # Initialize
        for call_id in range(1, 5):
            if call_id == 1:
                # Initialize on first call
                request = {
                    "jsonrpc": "2.0",
                    "id": call_id,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1.0"}
                    }
                }
            else:
                # Just echo request for other calls
                request = {
                    "jsonrpc": "2.0",
                    "id": call_id,
                    "method": "tools/list"
                }

            response = client.post("/mcp/request", json=request)
            assert response.status_code == 200
            assert response.json()["id"] == call_id

    def test_error_on_invalid_method(self, client):
        """Server returns error for invalid method."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid_method"
        }
        response = client.post("/mcp/request", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found

    def test_error_on_malformed_request(self, client):
        """Server returns error for malformed request."""
        request = {
            "id": 1,
            # Missing jsonrpc and method
        }
        response = client.post("/mcp/request", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    def test_mcp_protocol_version_validation(self, client):
        """Server validates protocol version."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-01-01",  # Wrong version
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        response = client.post("/mcp/request", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "protocol version" in data["error"]["message"].lower()

    def test_list_tools_format_json_schema(self, client):
        """Tool list includes proper JSON Schema."""
        response = client.get("/mcp/tools")
        data = response.json()

        # Find OCR tool
        ocr_tool = next((t for t in data["tools"] if t["name"] == "google_vision_ocr"), None)
        assert ocr_tool is not None

        # Verify schema
        assert "inputSchema" in ocr_tool
        schema = ocr_tool["inputSchema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "image_path" in schema["properties"]
        assert "required" in schema
        assert "image_path" in schema["required"]

    def test_custom_tool_registration(self):
        """Custom tools can be registered and discovered."""
        # Create a temporary registry with custom tool
        custom_registry = ToolRegistry()

        def custom_handler(args):
            return f"Custom result: {args.get('input')}"

        custom_registry.register_tool(
            "custom_tool",
            {
                "type": "object",
                "properties": {"input": {"type": "string"}},
                "required": ["input"]
            },
            custom_handler,
            description="A custom test tool"
        )

        # List tools
        tool_names = custom_registry.list_tools()
        assert "custom_tool" in tool_names

        # Get tool spec
        tool_spec = custom_registry.get_tool("custom_tool")
        assert tool_spec.name == "custom_tool"
        assert tool_spec.description == "A custom test tool"

        # Call tool
        result = custom_registry.call("custom_tool", {"input": "test"})
        assert result == "Custom result: test"
