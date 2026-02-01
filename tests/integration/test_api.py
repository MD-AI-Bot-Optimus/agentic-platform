import requests
import os

def test_run_workflow():
    url = "http://localhost:8000/run-workflow/"
    workflow_path = os.path.join(os.path.dirname(__file__), "../../demo_workflow.yaml")
    input_path = os.path.join(os.path.dirname(__file__), "../../demo_input.json")
    with open(workflow_path, "rb") as wf, open(input_path, "rb") as inp:
        files = {"workflow": wf, "input_artifact": inp}
        response = requests.post(url, files=files)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "audit_log" in data
        print("API test passed.")

if __name__ == "__main__":
    test_run_workflow()
