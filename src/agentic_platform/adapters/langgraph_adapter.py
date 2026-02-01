"""
Stub LangGraph Adapter for integration with LangGraph workflows.
"""

class LangGraphAdapter:
    def __init__(self, config=None):
        self.config = config

    def call(self, tool_name, args):
        raise NotImplementedError("LangGraphAdapter is not yet implemented.")
