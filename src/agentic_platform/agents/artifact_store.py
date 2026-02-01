import hashlib
import json

class InMemoryArtifactStore:
    def __init__(self):
        self._store = {}
    def put(self, job_id, artifact):
        if job_id in self._store:
            raise ValueError(f"Artifact for job {job_id} already exists")
        # Compute deterministic hash for artifact
        artifact_hash = hashlib.sha256(json.dumps(artifact, sort_keys=True).encode()).hexdigest()
        ref = f"artifact:{job_id}:{artifact_hash}"
        self._store[job_id] = (ref, artifact)
        return ref
    def get(self, ref):
        for job_id, (stored_ref, artifact) in self._store.items():
            if stored_ref == ref:
                return artifact
        raise KeyError(f"Artifact ref {ref} not found")
