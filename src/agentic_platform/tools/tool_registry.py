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
        def google_vision_ocr_handler(args):
            ocr = GoogleVisionOCR(credentials_json=args.get("credentials_json"))
            return ocr.ocr_image(args["image_path"])
        self.register_tool(
            "google_vision_ocr",
            ocr_schema,
            google_vision_ocr_handler,
            description="Extract text from images using Google Cloud Vision API"
        )

    def _register_mock_tools(self):
        """Register mock tools for testing agent flows."""
        # 1. Search Knowledge Base Tool
        search_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
        
        def search_handler(args):
            query = args.get("query", "").lower()
            if "neural network" in query:
                return "Found 5 articles: 'Neural Networks 101', 'Deep Learning Basics', 'Backpropagation Explained'. Summary: Neural networks are computing systems inspired by biological brains..."
            elif "transformer" in query:
                return "Found 3 articles: 'Attention Is All You Need', 'BERT Architecture', 'GPT Models'. Summary: Transformers use self-attention to process sequential data in parallel..."
            elif "langgraph" in query:
                return "Found documentation: LangGraph is a library for building stateful, multi-agent applications with LLMs..."
            else:
                return f"Found 2 general articles about '{query}'. They discuss basic concepts and history."
                
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
