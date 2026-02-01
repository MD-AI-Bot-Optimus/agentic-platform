"""
Policy enforcement for tools and models.
"""

from typing import List, Optional


class ToolAllowlistPolicy:
    """
    Enforces an allowlist of permitted tool/model names.
    """
    def __init__(self, allowed_tools: Optional[List[str]] = None):
        self.allowed_tools = set(allowed_tools) if allowed_tools else set()

    def is_tool_allowed(self, tool_name: str) -> bool:
        if not self.allowed_tools:
            return True  # If no allowlist, allow all
        return tool_name in self.allowed_tools

    def filter_allowed_tools(self, tool_names: List[str]) -> List[str]:
        if not self.allowed_tools:
            return tool_names
        return [t for t in tool_names if t in self.allowed_tools]

    def check(self, node: dict):
        """
        Checks if the node's model/tool is allowed. Raises PermissionError if not.
        """
        model = node.get("model")
        if not self.is_tool_allowed(model):
            raise PermissionError(f"Model/tool '{model}' is not allowed by policy.")
