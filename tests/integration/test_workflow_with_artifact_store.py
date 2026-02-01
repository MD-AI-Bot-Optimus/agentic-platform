from agentic_platform.adapters import s3_artifact_store
from agentic_platform.workflow import engine
from agentic_platform.audit.audit_log import InMemoryAuditLog

class S3AdapterWithAudit(s3_artifact_store.S3ArtifactStoreAdapter):
    def __init__(self, audit_log, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_log = audit_log
    def put(self, job_id, artifact):
        ref = super().put(job_id, artifact)
        self.audit_log.emit_event_with_artifact(self, ref)
        return ref

def test_workflow_engine_with_artifact_store():
    wf_def = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "step1", "type": "tool", "tool": "summarize", "model": "gpt-4"},
            {"id": "end", "type": "end"}
        ],
        "edges": [
            {"from": "start", "to": "step1"},
            {"from": "step1", "to": "end"}
        ]
    }
    audit_log = InMemoryAuditLog()
    artifact_store = S3AdapterWithAudit(audit_log)
    # Simulate storing artifact after tool call
    artifact = {"foo": "bar"}
    ref = artifact_store.put("job-1", artifact)
    loaded = artifact_store.get(ref)
    assert loaded == artifact
    # Check audit log for artifact event
    events = audit_log.get_events("job-1")
    assert any(getattr(e, "artifact_ref", None) == ref for e in events)
