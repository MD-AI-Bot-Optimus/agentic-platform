from typing import Callable, Dict, Any, List, Optional
import jsonschema

class ToolSpec:
    """Specification for a callable tool with schema validation."""
    def __init__(
        self,
        name: str,
        schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
        description: str = ""
    ):
        self.name = name
        self.schema = schema
        self.handler = handler
        self.description = description


from .google_vision_ocr import GoogleVisionOCR

class ToolRegistry:
    """Registry of available tools with schema validation.
    
    Manages tool registration, discovery, and execution with JSON schema validation.
    """
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._register_builtin_tools()
        self._register_mock_tools()

    def _register_builtin_tools(self):
        # Example: Register Google Vision OCR tool
        ocr_schema = {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "Path to the image file to OCR."},
                "credentials_json": {"type": "string", "description": "Path to Google credentials JSON file.", "default": None}
            },
            "required": ["image_path"]
        }
        
        # Lazy import to avoid circular dependencies if any
        from ..integrations.factory import get_ocr_provider
        
        def google_vision_ocr_handler(args):
            provider = get_ocr_provider(credentials_json=args.get("credentials_json"))
            return provider.ocr_image(args["image_path"])
            
        self.register_tool(
            "google_vision_ocr",
            ocr_schema,
            google_vision_ocr_handler,
            description="Extract text from images using Google Cloud Vision API (or Mock)"
        )

    def _register_mock_tools(self):
        """Register mock tools for testing agent flows."""
        # Register mock tools for UI Demos
        self.register_tool(
            name="process_data",
            handler=lambda args: f"Processed: {args.get('data', 'no-data')}",
            description="Mock tool for demo workflows (Identity).",
            schema={"type": "object", "properties": {"data": {"type": "string"}}}
        )
        
        self.register_tool(
            name="generate_summary",
            handler=lambda args: f"Summary of: {args.get('text', '')}",
            description="Mock tool for demo workflows (Summary).",
            schema={"type": "object", "properties": {"text": {"type": "string"}}}
        )
        
        self.register_tool(
            name="split_data",
            handler=lambda args: {"chunk_a": "data_A", "chunk_b": "data_B"},
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"data": {"type": "string"}}}
        )

        self.register_tool(
            name="process_chunk_a",
            handler=lambda args: f"Processed A: {args.get('chunk')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"chunk": {"type": "string"}}}
        )

        self.register_tool(
            name="process_chunk_b",
            handler=lambda args: f"Processed B: {args.get('chunk')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"chunk": {"type": "string"}}}
        )

        self.register_tool(
            name="merge_results",
            handler=lambda args: f"Merged: {args.get('res_a')} + {args.get('res_b')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"res_a": {"type": "string"}, "res_b": {"type": "string"}}}
        )

        # 1. Search Knowledge Base Tool
        search_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
        
        # Use Factory to get the configured provider (dynamically resolves tenant)
        from ..integrations.factory import get_knowledge_base_provider
        
        def search_handler(args):
            query = args.get("query", "")
            # Factory handles context resolution automatically now
            provider = get_knowledge_base_provider() 
            return provider.search(query)
                
        self.register_tool(
            "search_knowledge_base",
            search_schema,
            search_handler,
            description="Search the internal knowledge base for AI topics."
        )

    def register_tool(
        self,
        name: str,
        schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
        description: str = ""
    ) -> None:
        """Register a tool with the registry."""
        self._tools[name] = ToolSpec(name, schema, handler, description)

    def list_tools(self) -> List[str]:
        """Get list of tool names."""
        return list(self._tools.keys())

    def get_tool(self, name: str) -> Optional[ToolSpec]:
        """Get tool spec by name."""
        return self._tools.get(name)

    def call(self, name: str, args: Dict[str, Any]) -> Any:
        """Call a tool by name with the given arguments."""
        if name not in self._tools:
            raise Exception(f"Tool '{name}' not found")
        spec = self._tools[name]
        jsonschema.validate(instance=args, schema=spec.schema)
        return spec.handler(args)
