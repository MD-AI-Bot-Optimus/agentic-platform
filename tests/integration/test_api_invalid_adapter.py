import requests
import os

def test_run_workflow_invalid_adapter():
    url = "http://localhost:8002/run-workflow/"
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")
    with open(workflow_path, "rb") as wf, open(input_path, "rb") as inp:
        files = {"workflow": wf, "input_artifact": inp}
        data = {"adapter": "nonexistent"}
        response = requests.post(url, files=files, data=data)
        assert response.status_code == 400 or response.status_code == 422
        assert "Invalid adapter" in response.text or "not supported" in response.text
