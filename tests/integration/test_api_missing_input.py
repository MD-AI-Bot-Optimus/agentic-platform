import requests
import os

def test_run_workflow_missing_input():
    url = "http://localhost:8002/run-workflow/"
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    # Do not provide input_artifact
    with open(workflow_path, "rb") as wf:
        files = {"workflow": wf}
        response = requests.post(url, files=files)
        assert response.status_code == 400 or response.status_code == 422
        assert "Missing input" in response.text or "input_artifact" in response.text
