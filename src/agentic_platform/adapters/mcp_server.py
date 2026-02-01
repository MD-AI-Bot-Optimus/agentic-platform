"""
MCP (Model Context Protocol) Server Implementation.

This module implements an MCP server that exposes tools from ToolRegistry
to external MCP clients (e.g., Claude via Anthropic SDK).

MCP is a JSON-RPC 2.0 based protocol with three main operations:
1. initialize - Handshake and capability negotiation
2. tools/list - Discover available tools
3. tools/call - Execute a tool

This implementation integrates with the existing ToolRegistry to dynamically
expose all registered tools via the MCP protocol.

References:
- MCP Spec: https://modelcontextprotocol.io/
- JSON-RPC 2.0: https://www.jsonrpc.org/
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger("mcp_server")


@dataclass
class MCPTool:
    """MCP tool representation."""
    name: str
    description: str
    inputSchema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP protocol format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }


@dataclass
class MCPCapabilities:
    """MCP server capabilities advertised during initialization."""
    tools: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP protocol format."""
        return {
            k: v for k, v in {
                "tools": self.tools,
                "resources": self.resources,
                "prompts": self.prompts
            }.items() if v is not None
        }


class MCPError:
    """JSON-RPC 2.0 error representation."""

    # Standard JSON-RPC error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    def __init__(self, code: int, message: str, data: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error format."""
        error_dict = {
            "code": self.code,
            "message": self.message
        }
        if self.data:
            error_dict["data"] = self.data
        return error_dict


class MCPResponse:
    """JSON-RPC 2.0 response builder."""

    def __init__(self, request_id: Optional[int] = None):
        self.request_id = request_id

    def success(self, result: Any) -> Dict[str, Any]:
        """Build success response."""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if self.request_id is not None:
            response["id"] = self.request_id
        return response

    def error(self, error: MCPError) -> Dict[str, Any]:
        """Build error response."""
        response = {
            "jsonrpc": "2.0",
            "error": error.to_dict()
        }
        if self.request_id is not None:
            response["id"] = self.request_id
        return response


class MCPServer:
    """
    MCP server that exposes ToolRegistry tools via the MCP protocol.

    This server handles JSON-RPC 2.0 requests for:
    - initialize: Capability negotiation
    - tools/list: Tool discovery
    - tools/call: Tool execution

    Usage:
        server = MCPServer(tool_registry, version="1.0.0")
        response = server.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {...}
        })
    """

    # MCP Protocol version (date-based format per MCP spec)
    PROTOCOL_VERSION = "2025-06-18"

    def __init__(self, tool_registry: Any, version: str = "1.0.0"):
        """
        Initialize MCP server.

        Args:
            tool_registry: ToolRegistry instance with registered tools
            version: Server version for identification (e.g., "1.0.0")
        """
        self.tool_registry = tool_registry
        self.version = version
        self._initialized = False
        self._client_info: Optional[Dict[str, Any]] = None

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming JSON-RPC 2.0 request.

        Args:
            request: JSON-RPC request dict with jsonrpc, method, params, id

        Returns:
            JSON-RPC response dict with result/error and id

        Raises:
            ValueError: If request format is invalid
        """
        logger.debug(f"MCP request: {request}")

        # Validate JSON-RPC format
        if not isinstance(request, dict):
            return self._error_response(None, MCPError(
                MCPError.INVALID_REQUEST,
                "Request must be a JSON object"
            ))

        request_id = request.get("id")
        jsonrpc = request.get("jsonrpc")

        if jsonrpc != "2.0":
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_REQUEST,
                "jsonrpc field must be '2.0'"
            ))

        method = request.get("method")
        params = request.get("params", {})

        if not method:
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_REQUEST,
                "method field is required"
            ))

        # Route to handler
        try:
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            else:
                return self._error_response(request_id, MCPError(
                    MCPError.METHOD_NOT_FOUND,
                    f"Method '{method}' not found"
                ))
        except Exception as e:
            logger.error(f"Unhandled error in method '{method}'", exc_info=True)
            return self._error_response(request_id, MCPError(
                MCPError.INTERNAL_ERROR,
                str(e),
                {"details": str(e)}
            ))

    def _handle_initialize(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initialize request (lifecycle management).

        Client sends protocol version, capabilities, and info.
        Server responds with protocol version, capabilities, and info.
        """
        logger.info("Initialize request received")

        # Extract client info
        client_protocol_version = params.get("protocolVersion")
        client_capabilities = params.get("capabilities", {})
        client_info = params.get("clientInfo", {})

        # Version negotiation
        if client_protocol_version != self.PROTOCOL_VERSION:
            logger.warning(
                f"Protocol version mismatch: client={client_protocol_version}, "
                f"server={self.PROTOCOL_VERSION}"
            )
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_PARAMS,
                f"Protocol version mismatch. Server requires {self.PROTOCOL_VERSION}",
                {"client_version": client_protocol_version}
            ))

        # Store client info
        self._client_info = client_info
        self._initialized = True

        logger.info(f"Initialized with client: {client_info}")

        # Build server capabilities
        server_capabilities = MCPCapabilities(
            tools={"listChanged": True},  # Server supports tools/list_changed notification
            resources=None,  # Not supported yet
            prompts=None  # Not supported yet
        )

        # Build response
        result = {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": server_capabilities.to_dict(),
            "serverInfo": {
                "name": "agentic-platform-mcp-server",
                "version": self.version
            }
        }

        response = MCPResponse(request_id).success(result)
        logger.debug(f"Initialize response: {response}")
        return response

    def _handle_tools_list(self, request_id: int) -> Dict[str, Any]:
        """
        Handle tools/list request (tool discovery).

        Returns array of available tools with name, description, and inputSchema.
        """
        logger.info("Tools list request received")

        if not self._initialized:
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_REQUEST,
                "Must call initialize before tools/list"
            ))

        try:
            # Get tools from registry
            tool_names = self.tool_registry.list_tools()
            logger.debug(f"Available tools: {tool_names}")

            tools = []
            for tool_name in tool_names:
                try:
                    tool = self._convert_tool_to_mcp(tool_name)
                    tools.append(tool.to_dict())
                except Exception as e:
                    logger.error(f"Error converting tool '{tool_name}'", exc_info=True)
                    # Skip tools that fail conversion
                    continue

            result = {"tools": tools}
            response = MCPResponse(request_id).success(result)
            logger.debug(f"Tools list response: {len(tools)} tools")
            return response

        except Exception as e:
            logger.error("Error listing tools", exc_info=True)
            return self._error_response(request_id, MCPError(
                MCPError.INTERNAL_ERROR,
                str(e),
                {"details": "Failed to list tools"}
            ))

    def _handle_tools_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request (tool execution).

        Client specifies tool name and arguments. Server executes tool
        and returns result in content array format.
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call request: {tool_name}")
        logger.debug(f"Tool arguments: {arguments}")

        if not tool_name:
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_PARAMS,
                "Tool 'name' parameter is required"
            ))

        try:
            # Execute tool via registry
            start_time = datetime.now()
            result = self.tool_registry.call(tool_name, arguments)
            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info(f"Tool '{tool_name}' executed successfully in {elapsed:.2f}s")
            logger.debug(f"Tool result: {result}")

            # Format result as MCP content array
            # Tools can return various types; we'll convert to text for now
            if isinstance(result, dict) and "content" in result:
                # Already formatted
                content = result["content"]
            elif isinstance(result, str):
                content = [{"type": "text", "text": result}]
            else:
                # Convert to JSON string
                content = [{"type": "text", "text": json.dumps(result)}]

            mcp_result = {"content": content}
            response = MCPResponse(request_id).success(mcp_result)
            return response

        except ValueError as e:
            # Schema validation error
            logger.warning(f"Invalid arguments for tool '{tool_name}': {e}")
            return self._error_response(request_id, MCPError(
                MCPError.INVALID_PARAMS,
                f"Invalid arguments: {str(e)}",
                {"tool": tool_name}
            ))

        except Exception as e:
            # Tool execution error
            logger.error(f"Error executing tool '{tool_name}'", exc_info=True)
            return self._error_response(request_id, MCPError(
                MCPError.INTERNAL_ERROR,
                f"Tool execution failed: {str(e)}",
                {"tool": tool_name, "details": str(e)}
            ))

    def _convert_tool_to_mcp(self, tool_name: str) -> MCPTool:
        """
        Convert tool from registry format to MCP format.

        Extracts tool spec and converts its schema to MCP format.
        """
        # Get tool spec from registry
        tool_spec = self.tool_registry.get_tool(tool_name)
        
        if not tool_spec:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        return MCPTool(
            name=tool_spec.name,
            description=tool_spec.description or f"Tool: {tool_name}",
            inputSchema=tool_spec.schema
        )

    def _error_response(self, request_id: Optional[int], error: MCPError) -> Dict[str, Any]:
        """Build JSON-RPC error response."""
        return MCPResponse(request_id).error(error)
