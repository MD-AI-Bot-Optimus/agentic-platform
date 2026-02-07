from typing import Callable, Dict, Any, List, Optional
import jsonschema
from ..core.trace import add_trace_step

class ToolSpec:
    """Specification for a callable tool with schema validation."""
    def __init__(
        self,
        name: str,
        schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
        description: str = "",
        visible: bool = True
    ):
        self.name = name
        self.schema = schema
        self.handler = handler
        self.description = description
        self.visible = visible


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
            schema={"type": "object", "properties": {"data": {"type": "string"}}},
            visible=False
        )
        
        self.register_tool(
            name="generate_summary",
            handler=lambda args: f"Summary of: {args.get('text', '')}",
            description="Mock tool for demo workflows (Summary).",
            schema={"type": "object", "properties": {"text": {"type": "string"}}},
            visible=False
        )
        
        self.register_tool(
            name="split_data",
            handler=lambda args: {"chunk_a": "data_A", "chunk_b": "data_B"},
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"data": {"type": "string"}}},
            visible=False
        )

        self.register_tool(
            name="process_chunk_a",
            handler=lambda args: f"Processed A: {args.get('chunk')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"chunk": {"type": "string"}}},
            visible=False
        )

        self.register_tool(
            name="process_chunk_b",
            handler=lambda args: f"Processed B: {args.get('chunk')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"chunk": {"type": "string"}}},
            visible=False
        )

        self.register_tool(
            name="merge_results",
            handler=lambda args: f"Merged: {args.get('res_a')} + {args.get('res_b')}",
            description="Mock tool for parallel demo.",
            schema={"type": "object", "properties": {"res_a": {"type": "string"}, "res_b": {"type": "string"}}},
            visible=False
        )

        # Real Internet Research Tools
        
        # 1. DuckDuckGo Search
        ddg_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
        
        def ddg_handler(args):
            from duckduckgo_search import DDGS
            try:
                results = DDGS().text(args["query"], max_results=3)
                return str(results)
            except Exception as e:
                return f"Search failed: {str(e)}"

        self.register_tool(
            "internet_search", # Renamed from google_search for clarity, but agent might look for 'google_search' or 'web_search'
            ddg_schema,
            ddg_handler,
            description="Search the internet for real-time information (weather, news, flights)."
        )
        
        # Alias for commonly guessed names
        self.register_tool("google_search", ddg_schema, ddg_handler, description="Alias for internet search.", visible=False)
        self.register_tool("weather_api", ddg_schema, ddg_handler, description="Get weather via search.", visible=False)


        # 2. Wikipedia
        wiki_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Topic to search on Wikipedia."}
            },
            "required": ["query"]
        }
        
        def wikipedia_handler(args):
            import wikipedia
            try:
                # Limit to 2 sentences for brevity in demo
                return wikipedia.summary(args["query"], sentences=2)
            except Exception as e:
                return f"Wikipedia lookup failed: {str(e)}"

        self.register_tool(
            "wikipedia_lookup",
            wiki_schema,
            wikipedia_handler,
            description="Search Wikipedia for encyclopedic knowledge."
        )

        
        # 3. Simulated Booking (Wrapper around Search)
        # We can't really book flights, so we make this a "Research & Proposed Booking" tool
        flight_schema = {
            "type": "object", 
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "date": {"type": "string"}
            },
            "required": ["origin", "destination"]
        }
        
        def search_flight_handler(args):
            from duckduckgo_search import DDGS
            query = f"flights from {args.get('origin')} to {args.get('destination')} on {args.get('date', 'tomorrow')}"
            try:
                results = DDGS().text(query, max_results=2)
                return f"Found flight options via Search:\n{str(results)}"
            except Exception as e:
                return f"Flight search failed: {str(e)}"
                
        self.register_tool(
            "search_flights",
            flight_schema,
            search_flight_handler,
            description="Search for real flight options via the web.",
        )

        # We still need a 'book' tool to close the loop for the user's prompt
        self.register_tool(
            name="book_flight",
            handler=lambda args: f"Success! I have forwarded the booking request for {args.get('destination')} to the travel agent system (Simulation).",
            description="Execute the final flight booking.",
            schema={"type": "object", "properties": {"destination": {"type": "string"}, "flight_id": {"type": "string"}}},
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

        # 4. Stock Price Tool (Demo of Extensibility)
        stock_schema = {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, GOOGL)."}
            },
            "required": ["symbol"]
        }
        
        def stock_price_handler(args):
            import yfinance as yf
            symbol = args["symbol"].upper()
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period="1d")
                if history.empty:
                    return f"Could not find data for symbol {symbol}."
                price = history['Close'].iloc[-1]
                return f"The current price of {symbol} is ${price:.2f}."
            except Exception as e:
                return f"Stock lookup failed: {str(e)}"

        self.register_tool(
            "stock_price",
            stock_schema,
            stock_price_handler,
            description="Get the current stock price for a given symbol."
        )

        self.register_tool(
            "stock_price",
            stock_schema,
            stock_price_handler,
            description="Get the current stock price for a given symbol."
        )

        # 5. Code Interpreter (The "Magic" Tool)
        code_schema = {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The Python code to execute. Use print() to output results."}
            },
            "required": ["code"]
        }
        
        def python_interpreter_handler(args):
            import sys
            import io
            
            code = args["code"]
            # Create string buffers to capture output
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Save original stdout/stderr
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            try:
                # Redirect stdout/stderr
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                # Execute the code
                # simple mock context
                exec_globals = {"__builtins__": __builtins__, "sys": sys} 
                exec(code, exec_globals)
                
                # Get output
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
                
                result = ""
                if output:
                    result += f"Output:\n{output}"
                if error:
                    result += f"\nErrors:\n{error}"
                if not result:
                    result = "Code executed successfully (no output)."
                    
                return result
                
            except Exception as e:
                return f"Execution failed: {str(e)}"
            finally:
                # Restore stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr

        self.register_tool(
            "python_interpreter",
            code_schema,
            python_interpreter_handler,
            description="Execute Python code to solve math, data, or logic problems. Use print() to see results.",
            visible=False # Hidden from standard list, enabled via prompt
        )

    def register_tool(
        self,
        name: str,
        schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
        description: str = "",
        visible: bool = True
    ) -> None:
        """Register a tool with the registry."""
        self._tools[name] = ToolSpec(name, schema, handler, description, visible)

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
        
        add_trace_step("Tool Execution", f"Calling tool: {name}", f"Args: {list(args.keys())}")
        
        jsonschema.validate(instance=args, schema=spec.schema)
        return spec.handler(args)
