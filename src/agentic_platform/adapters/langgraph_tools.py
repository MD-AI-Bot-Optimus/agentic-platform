"""
LangGraph Tool Binding Layer

Converts our ToolRegistry tools to LangChain StructuredTool format.
Enables LangGraph agents to use tools autonomously.
"""

import logging
from typing import Dict, Any, List, Optional
from functools import wraps
from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolBinding:
    """Bind ToolRegistry tools to LangChain StructuredTool format."""
    
    @staticmethod
    def bind_tool(tool_name: str, tool_func, input_schema: Dict[str, Any]) -> StructuredTool:
        """
        Convert a tool function to LangChain StructuredTool.
        
        Args:
            tool_name: Name of the tool
            tool_func: Function to call
            input_schema: Pydantic model or dict describing inputs
        
        Returns:
            StructuredTool ready for LangChain agents
        """
        # Create Pydantic model from schema if dict
        if isinstance(input_schema, dict):
            # Convert dict schema to Pydantic model
            fields = {}
            for field_name, field_info in input_schema.items():
                field_type = field_info.get("type", str)
                field_desc = field_info.get("description", "")
                fields[field_name] = (field_type, Field(description=field_desc))
            
            input_model = type(f"{tool_name}Input", (BaseModel,), {
                "__annotations__": {k: v[0] for k, v in fields.items()},
                **{k: v[1] for k, v in fields.items()}
            })
        else:
            input_model = input_schema
        
        # Create StructuredTool
        structured_tool = StructuredTool(
            name=tool_name,
            func=tool_func,
            description=f"Executes {tool_name} tool",
            args_schema=input_model
        )
        
        logger.info(f"Bound tool: {tool_name}")
        return structured_tool
    
    @staticmethod
    def bind_ocr_tool(tool_client) -> StructuredTool:
        """Bind Google Vision OCR tool."""
        
        class OCRInput(BaseModel):
            image_path: str = Field(description="Path to image file")
        
        def ocr_func(image_path: str) -> Dict[str, Any]:
            """Extract text from image using OCR."""
            result = tool_client.call("google_vision_ocr", {"image_path": image_path})
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0),
                "symbols_count": result.get("symbols_count", 0)
            }
        
        return StructuredTool(
            name="extract_text_from_image",
            func=ocr_func,
            description="Extract text from an image using Google Vision API. Returns text content and confidence score.",
            args_schema=OCRInput
        )
    
    @staticmethod
    def bind_multiple_tools(tools_dict: Dict[str, tuple]) -> List[StructuredTool]:
        """
        Bind multiple tools.
        
        Args:
            tools_dict: {tool_name: (func, input_schema), ...}
        
        Returns:
            List of StructuredTools
        """
        bound_tools = []
        for tool_name, (func, schema) in tools_dict.items():
            try:
                tool = ToolBinding.bind_tool(tool_name, func, schema)
                bound_tools.append(tool)
            except Exception as e:
                logger.error(f"Failed to bind tool {tool_name}: {e}")
        
        return bound_tools


class ToolRegistry:
    """Simple tool registry for binding."""
    
    def __init__(self):
        self.tools: Dict[str, StructuredTool] = {}
    
    def register(self, name: str, func, input_schema: Dict[str, Any]) -> None:
        """Register a tool."""
        tool = ToolBinding.bind_tool(name, func, input_schema)
        self.tools[name] = tool
    
    def get_all(self) -> List[StructuredTool]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def get(self, name: str) -> Optional[StructuredTool]:
        """Get specific tool."""
        return self.tools.get(name)
