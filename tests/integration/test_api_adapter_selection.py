import requests
import os

def test_run_workflow_mcp():
    url = "http://localhost:8002/run-workflow/"
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")
    with open(workflow_path, "rb") as wf, open(input_path, "rb") as inp:
        files = {"workflow": wf, "input_artifact": inp}
        response = requests.post(url, files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["result"]
        assert data["audit_log"]
        found = False
        for tr in data.get("tool_results", []):
            if "MCP simulated response" in str(tr.get("result", "")):
                found = True
        assert found, "MCP tool result not found in tool_results"

def test_run_workflow_langgraph():
    url = "http://localhost:8002/run-workflow/"
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")
    with open(workflow_path, "rb") as wf, open(input_path, "rb") as inp:
        files = {"workflow": wf, "input_artifact": inp}
        data = {"adapter": "langgraph"}
        response = requests.post(url, files=files, data=data)
        assert response.status_code == 200
        data = response.json()
        assert data["result"]
        assert data["audit_log"]
        found = False
        for tr in data.get("tool_results", []):
            if "LangGraph simulated response" in str(tr.get("result", "")):
                found = True
        assert found, "LangGraph tool result not found in tool_results"
