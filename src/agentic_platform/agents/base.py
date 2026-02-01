class Agent:
    def __init__(self, name, version):
        self.name = name
        self.version = version

class ToolCallingAgent(Agent):
    def __init__(self, name, version, tool_client):
        super().__init__(name, version)
        self.tool_client = tool_client
    def run_tool(self, tool_name, args):
        return self.tool_client.call(tool_name, args)
