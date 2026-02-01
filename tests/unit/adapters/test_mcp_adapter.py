"""
Unit tests for MCPAdapter - tests MCP client behavior.

Covers:
- MCP client initialization and handshake
- Tool discovery via list_tools
- Tool execution via call_tool
- Error handling and error responses
- HTTP communication and retries
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import json

from agentic_platform.adapters.mcp_adapter import MCPAdapter, MCPClient


class TestMCPClient:
    """Test MCPClient HTTP communication."""

    def test_client_initialization(self):
        """MCPClient initializes with correct URL."""
        client = MCPClient("http://localhost:8002")
        assert client.base_url == "http://localhost:8002"
        assert client.timeout == 30

    def test_client_strips_trailing_slash(self):
        """MCPClient strips trailing slash from URL."""
        client = MCPClient("http://localhost:8002/")
        assert client.base_url == "http://localhost:8002"

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_initialize_request(self, mock_post):
        """Client sends initialize request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "test-server", "version": "1.0"}
            }
        }
        mock_post.return_value = mock_response

        client = MCPClient("http://localhost:8002")
        result = client.initialize()

        assert result["protocolVersion"] == "2025-06-18"
        assert client._initialized is True
        mock_post.assert_called_once()

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_list_tools_request(self, mock_post):
        """Client sends tools/list request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "tools": [
                    {
                        "name": "tool1",
                        "description": "Tool 1",
                        "inputSchema": {}
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        client = MCPClient("http://localhost:8002")
        client._initialized = True

        tools = client.list_tools()

        assert len(tools) == 1
        assert tools[0]["name"] == "tool1"

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_call_tool_request(self, mock_post):
        """Client sends tools/call request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {
                "content": [
                    {"type": "text", "text": "Tool result"}
                ]
            }
        }
        mock_post.return_value = mock_response

        client = MCPClient("http://localhost:8002")
        client._initialized = True

        result = client.call_tool("test_tool", {"arg": "value"})

        assert "content" in result
        assert result["content"][0]["text"] == "Tool result"

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_call_tool_with_error_response(self, mock_post):
        """Client raises error on MCP error response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 3,
            "error": {
                "code": -32603,
                "message": "Tool failed"
            }
        }
        mock_post.return_value = mock_response

        client = MCPClient("http://localhost:8002")
        client._initialized = True

        with pytest.raises(Exception, match="Tool failed"):
            client.call_tool("test_tool", {})

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_request_timeout(self, mock_post):
        """Client handles request timeout."""
        mock_post.side_effect = requests.exceptions.Timeout()

        client = MCPClient("http://localhost:8002")

        with pytest.raises(Exception, match="timeout"):
            client._send_request({"jsonrpc": "2.0", "method": "test"})

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_connection_error(self, mock_post):
        """Client handles connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        client = MCPClient("http://localhost:8002")

        with pytest.raises(Exception, match="Cannot connect"):
            client._send_request({"jsonrpc": "2.0", "method": "test"})

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_http_error(self, mock_post):
        """Client handles HTTP error."""
        mock_post.return_value.raise_for_status.side_effect = \
            requests.exceptions.HTTPError("500 Server Error")

        client = MCPClient("http://localhost:8002")

        with pytest.raises(Exception, match="MCP server error"):
            client._send_request({"jsonrpc": "2.0", "method": "test"})

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_invalid_json_response(self, mock_post):
        """Client handles invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
        mock_post.return_value = mock_response

        client = MCPClient("http://localhost:8002")

        with pytest.raises(Exception, match="invalid JSON"):
            client._send_request({"jsonrpc": "2.0", "method": "test"})


class TestMCPAdapter:
    """Test MCPAdapter tool execution."""

    def test_adapter_initialization(self):
        """MCPAdapter initializes with URL."""
        adapter = MCPAdapter("http://localhost:8002")
        assert adapter.mcp_server_url == "http://localhost:8002"
        assert isinstance(adapter.client, MCPClient)

    def test_adapter_default_url(self):
        """MCPAdapter uses default localhost URL."""
        adapter = MCPAdapter()
        assert adapter.mcp_server_url == "http://localhost:8002"

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool(self, mock_call):
        """Adapter calls tool via client."""
        mock_call.return_value = {
            "content": [
                {"type": "text", "text": "Result"}
            ]
        }

        adapter = MCPAdapter("http://localhost:8002")
        result = adapter.call("test_tool", {"arg": "value"})

        assert result == "Result"
        mock_call.assert_called_once_with("test_tool", {"arg": "value"})

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool_with_dict_content(self, mock_call):
        """Adapter extracts dict content correctly."""
        mock_call.return_value = {
            "content": [
                {"type": "object", "data": {"key": "value"}}
            ]
        }

        adapter = MCPAdapter()
        result = adapter.call("test_tool", {})

        assert result == {"type": "object", "data": {"key": "value"}}

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool_empty_content(self, mock_call):
        """Adapter handles empty content."""
        mock_call.return_value = {"content": []}

        adapter = MCPAdapter()
        result = adapter.call("test_tool", {})

        assert result == ""

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool_error(self, mock_call):
        """Adapter propagates tool execution errors."""
        mock_call.side_effect = Exception("Tool failed")

        adapter = MCPAdapter()

        with pytest.raises(Exception, match="Tool failed"):
            adapter.call("test_tool", {})

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.list_tools")
    def test_list_tools(self, mock_list):
        """Adapter lists available tools."""
        mock_list.return_value = [
            {"name": "tool1", "description": "Tool 1"},
            {"name": "tool2", "description": "Tool 2"}
        ]

        adapter = MCPAdapter()
        tools = adapter.list_tools()

        assert tools == ["tool1", "tool2"]

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.list_tools")
    def test_list_tools_error(self, mock_list):
        """Adapter handles list_tools errors."""
        mock_list.side_effect = Exception("Connection failed")

        adapter = MCPAdapter()

        with pytest.raises(Exception, match="Connection failed"):
            adapter.list_tools()

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool_extracts_text_from_content(self, mock_call):
        """Adapter properly extracts text from content array."""
        mock_call.return_value = {
            "content": [
                {
                    "type": "text",
                    "text": "Multi\nLine\nText"
                }
            ]
        }

        adapter = MCPAdapter()
        result = adapter.call("ocr", {"image_path": "/path/to/image"})

        assert result == "Multi\nLine\nText"

    @patch("agentic_platform.adapters.mcp_adapter.MCPClient.call_tool")
    def test_call_tool_handles_raw_string_in_content(self, mock_call):
        """Adapter handles raw string in content."""
        mock_call.return_value = {
            "content": ["Raw string result"]
        }

        adapter = MCPAdapter()
        result = adapter.call("tool", {})

        assert result == "Raw string result"


class TestMCPAdapterIntegration:
    """Test MCPAdapter with real-like scenarios."""

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_end_to_end_ocr_call(self, mock_post):
        """End-to-end OCR call through adapter."""
        responses = [
            # Initialize response
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "serverInfo": {"name": "mcp", "version": "1.0"}
                }
            },
            # Tool call response
            {
                "jsonrpc": "2.0",
                "id": 3,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": "Extracted text from OCR"
                        }
                    ]
                }
            }
        ]

        mock_response = Mock()
        mock_response.json.side_effect = responses
        mock_post.return_value = mock_response

        adapter = MCPAdapter("http://localhost:8002")
        result = adapter.call("google_vision_ocr", {"image_path": "/path/to/image.jpg"})

        assert result == "Extracted text from OCR"
        assert mock_post.call_count == 2  # initialize + call_tool

    @patch("agentic_platform.adapters.mcp_adapter.requests.post")
    def test_adapter_retries_initialization(self, mock_post):
        """Adapter auto-initializes if not initialized."""
        responses = [
            # Initialize response
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"protocolVersion": "2025-06-18", "capabilities": {}}
            },
            # Tool call response
            {
                "jsonrpc": "2.0",
                "id": 3,
                "result": {
                    "content": [{"type": "text", "text": "result"}]
                }
            }
        ]

        mock_response = Mock()
        mock_response.json.side_effect = responses
        mock_post.return_value = mock_response

        adapter = MCPAdapter()
        # First call should auto-initialize
        result = adapter.call("tool", {})

        assert result == "result"
        assert mock_post.call_count == 2
