class InMemoryAgentRegistry:
    def __init__(self):
        self._agents = {}
    def register(self, agent):
        key = (agent.name, agent.version)
        if key in self._agents:
            raise ValueError(f"Agent {key} already registered")
        self._agents[key] = agent
    def get(self, name, version):
        return self._agents.get((name, version))
    def list(self):
        return list(self._agents.values())
