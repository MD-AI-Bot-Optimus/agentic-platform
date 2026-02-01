"""
Stub DB Artifact Store Adapter for integration with database storage.
"""

class DBArtifactStoreAdapter:
    def __init__(self, config=None):
        self.config = config

    def put(self, job_id, artifact):
        raise NotImplementedError("DBArtifactStoreAdapter is not yet implemented.")

    def get(self, ref):
        raise NotImplementedError("DBArtifactStoreAdapter is not yet implemented.")
