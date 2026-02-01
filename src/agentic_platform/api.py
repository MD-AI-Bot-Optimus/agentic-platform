from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import yaml
import json
from agentic_platform.workflow import engine
from agentic_platform.audit.audit_log import InMemoryAuditLog
from agentic_platform.adapters.mcp_adapter import MCPAdapter

app = FastAPI()

@app.post("/run-workflow/")
async def run_workflow(
    workflow: UploadFile = File(...),
    input_artifact: UploadFile = File(...)
):
    wf_def = yaml.safe_load(await workflow.read())
    input_data = json.loads((await input_artifact.read()).decode())
    audit_log = InMemoryAuditLog()
    tool_client = MCPAdapter()
    result = engine.run(wf_def, input_artifact=input_data, tool_client=tool_client, audit_log=audit_log)
    audit_events = [vars(e) for e in audit_log.get_events("job-1")]
    return JSONResponse({"result": result, "audit_log": audit_events})
