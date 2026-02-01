"""
Stub S3 Artifact Store Adapter for integration with S3-compatible storage.
"""


class S3ArtifactStoreAdapter:
    def __init__(self, config=None):
        self.config = config or {}
        self._store = {}

    def put(self, job_id, artifact):
        # Simulate storing artifact in S3 by storing in memory
        ref = f"s3://{job_id}/{len(self._store)}"
        self._store[ref] = artifact
        return ref

    def get(self, ref):
        # Simulate retrieving artifact from S3
        return self._store.get(ref)
