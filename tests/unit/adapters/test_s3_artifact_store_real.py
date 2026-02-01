from agentic_platform.adapters import s3_artifact_store

def test_s3_artifact_store_adapter_real():
    store = s3_artifact_store.S3ArtifactStoreAdapter()
    job_id = "job-abc"
    artifact = {"foo": "bar"}
    ref = store.put(job_id, artifact)
    assert ref.startswith("s3://job-abc/")
    loaded = store.get(ref)
    assert loaded == artifact
