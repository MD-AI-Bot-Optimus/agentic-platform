"""
MCP (Model Context Protocol) Adapter for tool execution.

This adapter can call tools either via:
1. A remote MCP server (HTTP)
2. A local MCP server (for testing)

Usage:
    adapter = MCPAdapter("http://localhost:8002")  # Remote server
    adapter = MCPAdapter()  # Local server (fallback)
    result = adapter.call("google_vision_ocr", {"image_path": "/path/to/image.jpg"})
"""

import logging
import requests
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

logger = logging.getLogger("mcp_adapter")


class MCPClient:
    """HTTP client for MCP protocol."""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize MCP client.

        Args:
            base_url: Base URL of MCP server (e.g., http://localhost:8002)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._initialized = False

    def initialize(self) -> Dict[str, Any]:
        """Send initialize request to MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "agentic-platform-client",
                    "version": "1.0.0"
                }
            }
        }

        response = self._send_request(request)
        self._initialized = True
        return response.get("result", {})

    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server."""
        if not self._initialized:
            self.initialize()

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        response = self._send_request(request)
        return response.get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool via MCP server."""
        if not self._initialized:
            self.initialize()

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = self._send_request(request)

        # Handle error response
        if "error" in response:
            error = response["error"]
            raise Exception(f"MCP error: {error.get('message')} ({error.get('code')})")

        return response.get("result", {})

    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server."""
        url = urljoin(self.base_url, "/mcp/request")

        logger.debug(f"MCP request: {request}")

        try:
            response = requests.post(
                url,
                json=request,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            logger.debug(f"MCP response: {result}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"MCP request timeout: {url}")
            raise Exception(f"MCP server timeout at {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"MCP connection error: {url}")
            raise Exception(f"Cannot connect to MCP server at {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"MCP HTTP error: {e}")
            raise Exception(f"MCP server error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"MCP invalid JSON response: {e}")
            raise Exception(f"MCP server returned invalid JSON: {e}")


class MCPAdapter:
    """Adapter for calling tools via MCP protocol."""

    def __init__(self, mcp_server_url: Optional[str] = None):
        """
        Initialize MCP adapter.

        Args:
            mcp_server_url: URL of MCP server (e.g., http://localhost:8002)
                          If None, uses default localhost:8002
        """
        self.mcp_server_url = mcp_server_url or "http://localhost:8002"
        self.client = MCPClient(self.mcp_server_url)

    def call(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Call a tool via MCP server.

        Args:
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool

        Returns:
            Tool result (extracted from MCP content array)

        Raises:
            Exception: If tool call fails
        """
        logger.info(f"Calling tool via MCP: {tool_name}")
        logger.debug(f"Tool arguments: {args}")

        try:
            # Call tool via MCP
            result = self.client.call_tool(tool_name, args)

            # Extract content from MCP response
            # MCP returns: {"content": [{"type": "text", "text": "..."}]}
            content = result.get("content", [])

            if not content:
                logger.warning(f"Tool returned empty content: {tool_name}")
                return ""

            # For now, assume first content item is the main result
            # In future, could support multiple content types
            first_content = content[0]

            if isinstance(first_content, dict):
                # If it's already a dict, extract text or return as-is
                if "text" in first_content:
                    return first_content["text"]
                else:
                    return first_content

            return first_content

        except Exception as e:
            logger.error(f"MCP call failed for tool '{tool_name}'", exc_info=True)
            raise

    def list_tools(self) -> List[str]:
        """Get list of available tools."""
        logger.info("Listing tools via MCP")

        try:
            tools = self.client.list_tools()
            tool_names = [tool["name"] for tool in tools]
            logger.debug(f"Available tools: {tool_names}")
            return tool_names
        except Exception as e:
            logger.error("Failed to list tools", exc_info=True)
            raise

