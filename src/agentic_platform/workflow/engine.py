from agentic_platform.core.types import AuditEvent

def run(wf_def, input_artifact, tool_client, audit_log, stop_at_node=None, return_state=False, resume_state=None):
    job_id = "job-1"  # In real code, generate unique job id
    node_map = {n["id"]: n for n in wf_def["nodes"]}
    edges = wf_def["edges"]
    if resume_state is not None:
        current = node_map[resume_state["current_node_id"]]
        visited = set(resume_state.get("visited", []))
        # Remove current node from visited to avoid immediate cycle detection
        node_key = (current["id"],)
        if node_key in visited:
            visited.remove(node_key)
    else:
        current = next(n for n in wf_def["nodes"] if n["type"] == "start")
        visited = set()
        audit_log.emit(AuditEvent(
            event_type="STEP_STARTED",
            job_id=job_id,
            node_id=current["id"],
            timestamp="2026-01-31T00:00:00Z",
            status="started"
        ))
    status = "running"
    used_persistence = return_state or resume_state is not None
    while current["type"] != "end":
        node_key = (current["id"],)
        if node_key in visited:
            raise RuntimeError(f"Cycle detected at node {current['id']}")
        visited.add(node_key)
        if stop_at_node is not None and current["id"] == stop_at_node:
            # Save state and return
            state = {"current_node_id": current["id"], "visited": list(visited)}
            if return_state:
                return {"job_id": job_id, "status": "paused"}, state
            else:
                return {"job_id": job_id, "status": "paused"}
        # Find all outgoing edges
        outgoing = [e for e in edges if e["from"] == current["id"]]
        # Select edge: if any edge has a 'condition', evaluate it
        next_edge = None
        for e in outgoing:
            cond = e.get("condition")
            if cond is None:
                # unconditional edge
                if next_edge is None:
                    next_edge = e
            else:
                try:
                    if eval(cond, {"__builtins__": {}}, {"input": input_artifact}):
                        next_edge = e
                        break
                except Exception:
                    pass
        if next_edge is None:
            raise RuntimeError(f"No valid outgoing edge from node {current['id']} for input {input_artifact}")
        next_node = node_map[next_edge["to"]]
        if next_node["type"] == "tool":
            audit_log.emit(AuditEvent(
                event_type="STEP_STARTED",
                job_id=job_id,
                node_id=next_node["id"],
                timestamp="2026-01-31T00:00:01Z",
                status="started"
            ))
            try:
                tool_client.call(next_node["tool"], {})
                audit_log.emit(AuditEvent(
                    event_type="STEP_ENDED",
                    job_id=job_id,
                    node_id=next_node["id"],
                    timestamp="2026-01-31T00:00:02Z",
                    status="ended"
                ))
            except Exception as e:
                audit_log.emit(AuditEvent(
                    event_type="STEP_ERRORED",
                    job_id=job_id,
                    node_id=next_node["id"],
                    timestamp="2026-01-31T00:00:02Z",
                    status="errored"
                ))
                raise
        current = next_node
    status = "completed"
    audit_log.emit(AuditEvent(
        event_type="STEP_ENDED",
        job_id=job_id,
        node_id=current["id"],
        timestamp="2026-01-31T00:00:03Z",
        status="ended"
    ))
    if used_persistence:
        return {"job_id": job_id, "status": status}, None
    return {"job_id": job_id, "status": status}
