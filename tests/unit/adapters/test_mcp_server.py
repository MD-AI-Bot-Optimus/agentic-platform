"""
Unit tests for MCPServer - tests tool discovery and execution.

Covers:
- Tool list generation in MCP format
- Tool schema conversion
- Tool execution with valid/invalid arguments
- Error handling and MCP error responses
- Initialization and capability negotiation
"""

import pytest
import json
from unittest.mock import Mock, MagicMock

from agentic_platform.adapters.mcp_server import (
    MCPServer,
    MCPTool,
    MCPCapabilities,
    MCPError,
    MCPResponse
)
from agentic_platform.tools.tool_registry import ToolSpec


class TestMCPError:
    """Test MCPError and error formatting."""

    def test_error_with_code_and_message(self):
        """MCPError stores code and message."""
        error = MCPError(MCPError.INVALID_PARAMS, "Invalid parameters")
        assert error.code == MCPError.INVALID_PARAMS
        assert error.message == "Invalid parameters"

    def test_error_to_dict(self):
        """MCPError.to_dict() returns proper format."""
        error = MCPError(MCPError.INVALID_PARAMS, "Test error")
        error_dict = error.to_dict()

        assert error_dict["code"] == MCPError.INVALID_PARAMS
        assert error_dict["message"] == "Test error"

    def test_error_with_data(self):
        """MCPError can include additional data."""
        data = {"details": "Something went wrong"}
        error = MCPError(MCPError.INTERNAL_ERROR, "Error", data)
        error_dict = error.to_dict()

        assert error_dict["data"] == data


class TestMCPResponse:
    """Test MCPResponse builders."""

    def test_success_response(self):
        """Success response has correct structure."""
        response = MCPResponse(request_id=123)
        result = response.success({"tools": []})

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 123
        assert result["result"] == {"tools": []}

    def test_error_response(self):
        """Error response has correct structure."""
        error = MCPError(MCPError.METHOD_NOT_FOUND, "Method not found")
        response = MCPResponse(request_id=456)
        result = response.error(error)

        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 456
        assert result["error"]["code"] == MCPError.METHOD_NOT_FOUND


class TestMCPTool:
    """Test MCPTool representation."""

    def test_tool_to_dict(self):
        """MCPTool.to_dict() returns MCP format."""
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            inputSchema={"type": "object", "properties": {}}
        )
        tool_dict = tool.to_dict()

        assert tool_dict["name"] == "test_tool"
        assert tool_dict["description"] == "Test tool"
        assert tool_dict["inputSchema"]["type"] == "object"


class TestMCPCapabilities:
    """Test MCPCapabilities."""

    def test_capabilities_to_dict(self):
        """MCPCapabilities.to_dict() only includes non-None fields."""
        caps = MCPCapabilities(tools={"listChanged": True})
        caps_dict = caps.to_dict()

        assert "tools" in caps_dict
        assert "resources" not in caps_dict
        assert "prompts" not in caps_dict


class TestMCPServerInitialization:
    """Test MCPServer initialization request handling."""

    def test_initialize_request(self):
        """Server handles initialize request."""
        registry = Mock()
        registry.list_tools.return_value = []

        server = MCPServer(registry)
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

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2025-06-18"
        assert response["result"]["capabilities"]["tools"]["listChanged"] is True

    def test_initialize_protocol_version_mismatch(self):
        """Server rejects incompatible protocol version."""
        registry = Mock()
        server = MCPServer(registry)
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

        response = server.handle_request(request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.INVALID_PARAMS


class TestMCPServerToolsList:
    """Test MCPServer tools/list request handling."""

    def test_tools_list_before_initialize(self):
        """Server requires initialize before tools/list."""
        registry = Mock()
        server = MCPServer(registry)

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        response = server.handle_request(request)

        assert "error" in response
        assert "initialize" in response["error"]["message"].lower()

    def test_tools_list_after_initialize(self):
        """Server returns tools list after initialize."""
        registry = Mock()
        tool_spec = ToolSpec(
            name="test_tool",
            schema={"type": "object", "properties": {}, "required": []},
            handler=lambda x: "result",
            description="A test tool"
        )
        registry.list_tools.return_value = ["test_tool"]
        registry.get_tool.return_value = tool_spec

        server = MCPServer(registry)

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
        server.handle_request(init_request)

        # Now list tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = server.handle_request(list_request)

        assert "result" in response
        assert "tools" in response["result"]
        tools = response["result"]["tools"]
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
        assert tools[0]["description"] == "A test tool"

    def test_tools_list_empty_registry(self):
        """Server returns empty list when no tools registered."""
        registry = Mock()
        registry.list_tools.return_value = []

        server = MCPServer(registry)

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
        server.handle_request(init_request)

        # List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = server.handle_request(list_request)

        assert response["result"]["tools"] == []


class TestMCPServerToolCall:
    """Test MCPServer tools/call request handling."""

    def test_tools_call_with_valid_arguments(self):
        """Server executes tool with valid arguments."""
        registry = Mock()
        registry.call.return_value = {"text": "OCR result"}

        tool_spec = ToolSpec(
            name="test_tool",
            schema={
                "type": "object",
                "properties": {"arg": {"type": "string"}},
                "required": ["arg"]
            },
            handler=lambda x: "result",
            description="Test"
        )
        registry.get_tool.return_value = tool_spec
        registry.list_tools.return_value = ["test_tool"]

        server = MCPServer(registry)

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
        server.handle_request(init_request)

        # Call tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"arg": "value"}
            }
        }
        response = server.handle_request(call_request)

        assert "result" in response
        assert "content" in response["result"]
        registry.call.assert_called_once_with("test_tool", {"arg": "value"})

    def test_tools_call_formats_text_result(self):
        """Server formats text result in MCP content array."""
        registry = Mock()
        registry.call.return_value = "Simple text result"

        tool_spec = ToolSpec(
            name="test_tool",
            schema={"type": "object"},
            handler=lambda x: "result",
            description="Test"
        )
        registry.get_tool.return_value = tool_spec

        server = MCPServer(registry)

        # Initialize
        server._initialized = True
        server._client_info = {}

        # Call tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {}
            }
        }
        response = server.handle_request(call_request)

        content = response["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "Simple text result"

    def test_tools_call_missing_tool_name(self):
        """Server returns error if tool name missing."""
        registry = Mock()
        server = MCPServer(registry)
        server._initialized = True

        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"arguments": {}}  # Missing 'name'
        }
        response = server.handle_request(call_request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.INVALID_PARAMS

    def test_tools_call_tool_not_found(self):
        """Server returns error if tool not found."""
        registry = Mock()
        registry.call.side_effect = Exception("Tool 'unknown' not found")

        server = MCPServer(registry)
        server._initialized = True

        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        response = server.handle_request(call_request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.INTERNAL_ERROR


class TestMCPServerErrorHandling:
    """Test MCP error handling."""

    def test_invalid_json_rpc_format(self):
        """Server rejects invalid JSON-RPC format."""
        registry = Mock()
        server = MCPServer(registry)

        # Missing jsonrpc field
        request = {
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = server.handle_request(request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.INVALID_REQUEST

    def test_missing_method(self):
        """Server rejects request with missing method."""
        registry = Mock()
        server = MCPServer(registry)

        request = {
            "jsonrpc": "2.0",
            "id": 1
        }
        response = server.handle_request(request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.INVALID_REQUEST

    def test_unknown_method(self):
        """Server rejects unknown method."""
        registry = Mock()
        server = MCPServer(registry)

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown_method"
        }
        response = server.handle_request(request)

        assert "error" in response
        assert response["error"]["code"] == MCPError.METHOD_NOT_FOUND

    def test_request_not_dict(self):
        """Server rejects non-dict request."""
        registry = Mock()
        server = MCPServer(registry)

        response = server.handle_request("not a dict")

        assert "error" in response
        assert response["error"]["code"] == MCPError.INVALID_REQUEST


class TestMCPServerToolConversion:
    """Test tool schema conversion to MCP format."""

    def test_convert_tool_to_mcp(self):
        """Tool spec converted to MCP format."""
        registry = Mock()
        tool_spec = ToolSpec(
            name="ocr",
            schema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"}
                },
                "required": ["image_path"]
            },
            handler=lambda x: {},
            description="OCR tool"
        )
        registry.get_tool.return_value = tool_spec

        server = MCPServer(registry)
        mcp_tool = server._convert_tool_to_mcp("ocr")

        assert mcp_tool.name == "ocr"
        assert mcp_tool.description == "OCR tool"
        assert mcp_tool.inputSchema["type"] == "object"
        assert "image_path" in mcp_tool.inputSchema["properties"]

    def test_convert_tool_not_found(self):
        """Error when converting non-existent tool."""
        registry = Mock()
        registry.get_tool.return_value = None

        server = MCPServer(registry)

        with pytest.raises(ValueError, match="not found"):
            server._convert_tool_to_mcp("unknown")
