from typing import Callable, Dict, Any, List
import jsonschema

class ToolSpec:
    def __init__(self, name: str, schema: Dict[str, Any], handler: Callable[[Dict[str, Any]], Any]):
        self.name = name
        self.schema = schema
        self.handler = handler

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}

    def register_tool(self, name: str, schema: Dict[str, Any], handler: Callable[[Dict[str, Any]], Any]):
        self._tools[name] = ToolSpec(name, schema, handler)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def call(self, name: str, args: Dict[str, Any]) -> Any:
        if name not in self._tools:
            raise Exception(f"Tool '{name}' not found")
        spec = self._tools[name]
        jsonschema.validate(instance=args, schema=spec.schema)
        return spec.handler(args)
