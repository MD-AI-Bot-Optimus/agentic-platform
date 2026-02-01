# Minimal FastAPI REST API for workflow execution

## Overview
This API allows you to execute a workflow by uploading a YAML workflow definition and a JSON input artifact. It returns the workflow result and the audit log.

### Endpoint
- **POST** `/run-workflow/`
  - **Request:**
    - `workflow`: YAML file (multipart/form-data)
    - `input_artifact`: JSON file (multipart/form-data)
  - **Response:**
    - `result`: Output of the workflow
    - `audit_log`: List of audit events

### Usage Example
1. Start the API:
   ```sh
   uvicorn src.agentic_platform.api:app --reload
   ```
2. Run the integration test or use curl:
   ```sh
   curl -F "workflow=@demo_workflow.yaml" -F "input_artifact=@demo_input.json" http://localhost:8000/run-workflow/
   ```

### Test
- See `tests/integration/test_api.py` for an automated test example.

### Implementation Notes
- The API uses the same engine and adapters as the CLI.
- Audit log is returned for transparency and debugging.
