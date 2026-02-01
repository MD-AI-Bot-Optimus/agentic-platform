class ModelRouter:
    def __init__(self, model_clients):
        self.model_clients = model_clients
        self.default_model = next(iter(model_clients))
    def call(self, node, prompt, args):
        model = node.get("model", self.default_model)
        client = self.model_clients[model]
        return client.call(prompt, args)
