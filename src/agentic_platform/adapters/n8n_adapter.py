"""
Stub n8n Adapter for integration with n8n workflows.
"""

class N8NAdapter:
    def __init__(self, config=None):
        self.config = config

    def call(self, tool_name, args):
        raise NotImplementedError("N8NAdapter is not yet implemented.")
