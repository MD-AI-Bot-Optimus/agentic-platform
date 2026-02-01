import requests
import os

def test_run_workflow_malformed_workflow():
    url = "http://localhost:8002/run-workflow/"
    # Malformed workflow YAML
    workflow_path = os.path.join(os.path.dirname(__file__), "malformed_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")
    with open(workflow_path, "w") as wf:
        wf.write("not: valid: yaml: - [missing structure]")
    with open(workflow_path, "rb") as wf, open(input_path, "rb") as inp:
        files = {"workflow": wf, "input_artifact": inp}
        response = requests.post(url, files=files)
        assert response.status_code == 400 or response.status_code == 422
        assert "Malformed workflow YAML" in response.text or "Invalid workflow" in response.text or "malformed" in response.text
    os.remove(workflow_path)
