
# Minimal FastAPI REST API for workflow execution & Modern React UI

## Overview
This API allows you to execute workflows and perform OCR on images. It provides endpoints for:
1. **OCR (Optical Character Recognition):** Extract text from images using Google Vision API
2. **Workflow Execution:** Execute YAML-defined workflows with pluggable adapters

## Endpoints

### 1. OCR Endpoint (MCP Protocol)
- **POST** `/mcp/request`
  - **Description:** Extract text and confidence from images via MCP JSON-RPC 2.0
  - **Request Body:**
    ```json
    {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "google_vision_ocr",
        "arguments": {
          "image_path": "sample_data/stock_gs200.jpg"
        }
      },
      "id": 1
    }
    ```
  - **Response:**
    ```json
    {
      "jsonrpc": "2.0",
      "result": {
        "text": "Extracted text from image...",
        "confidence": 0.95
      },
      "id": 1
    }
    ```
  - **Confidence Behavior:**
    - **Simple documents** (letters, etc.): `1.0` (high confidence)
    - **Hard-to-read documents** (blurry, handwriting): `0.2-0.4` (averaged individual symbol confidences)
    - **Complex layouts** (financial tables >150 symbols, all zero confidence): `0.95` (layout complexity factor)
  - **Authentication:** Uses Application Default Credentials (ADC) from Google Cloud SDK
  - **Example:**
    ```bash
    curl -X POST http://localhost:8000/mcp/request \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
          "name": "google_vision_ocr",
          "arguments": {"image_path": "sample_data/letter.jpg"}
        },
        "id": 1
      }'
    ```
- **GET** `/mcp/tools`
  - **Description:** List all available MCP tools with metadata
  - **Example Response:**
    ```json
    {
      "tools": [
        {
          "name": "google_vision_ocr",
          "description": "Extract text from images using Google Cloud Vision API",
          "inputSchema": {
            "type": "object",
            "properties": {
              "image_path": {
                "type": "string",
                "description": "Path to the image file to OCR."
              },
              "credentials_json": {
                "type": "string",
                "description": "Path to Google credentials JSON file.",
                "default": null
              }
            },
            "required": ["image_path"]
          }
        }
      ]
    }
    ```
  - **cURL Example:**
    ```bash
    curl http://localhost:8002/mcp/tools
    ```

### 3. MCP Tool Execution Endpoint
- **POST** `/mcp/request`
  - **Description:** Execute a tool via JSON-RPC 2.0 MCP protocol
  - **Request Body:** JSON-RPC 2.0 request
    ```json
    {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "google_vision_ocr",
        "arguments": {
          "image_path": "/path/to/image.jpg"
        }
      },
      "id": 1
    }
    ```
  - **Response:** JSON-RPC 2.0 response with tool result or error
    ```json
    {
      "jsonrpc": "2.0",
      "result": {
        "text": "Extracted text content",
        "confidence": 0.95,
        "formatted_text_lines": ["Line 1", "Line 2", "..."]
      },
      "id": 1
    }
    ```
  - **Error Response:**
    ```json
    {
      "jsonrpc": "2.0",
      "error": {
        "code": -32602,
        "message": "Invalid params",
        "data": "Tool 'unknown_tool' not found in registry"
      },
      "id": 1
    }
    ```
  - **cURL Example:**
    ```bash
    curl -X POST http://localhost:8002/mcp/request \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
          "name": "google_vision_ocr",
          "arguments": {"image_path": "/sample_data/ocr_sample_plaid.jpg"}
        },
        "id": 1
      }'
    ```
  - **Supported Methods:**
    - `tools/call` - Execute a tool with arguments
    - `tools/list` - List all available tools (via GET `/mcp/tools` endpoint instead)
  - **Error Codes:**
    - `-32700`: Parse error
    - `-32600`: Invalid Request
    - `-32601`: Method not found
    - `-32602`: Invalid params
    - `-32603`: Internal error


### Usage Example
1. Start all services:
  ```sh
  ./start_all.sh
  ```
  - This launches the backend API (port 8002) and the React UI (port 5173).

2. **List Available Tools:**
  ```bash
  curl http://localhost:8002/mcp/tools
  ```

3. **Call Tool via MCP:**
  ```bash
  curl -X POST http://localhost:8002/mcp/request \
    -H "Content-Type: application/json" \
    -d '{
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "google_vision_ocr",
        "arguments": {"image_path": "/sample_data/ocr_sample_plaid.jpg"}
      },
      "id": 1
    }'
  ```

4. **OCR via UI:** Open http://localhost:5174, go to "OCR Demo" section, upload an image, and see extracted text.

5. **OCR via cURL:**
  ```sh
  curl -X POST http://localhost:8002/run-ocr/ \
    -F "image=@sample_data/ocr_sample_plaid.jpg"
  ```

6. **MCP Tool Tester via UI:** Open http://localhost:5174, go to "MCP Tool Tester" section, select a tool, input JSON arguments, and call.

7. **Workflow via UI:** Upload YAML workflow and JSON input, select adapter, and run.

8. **Workflow via cURL:**
  ```sh
  curl -F "workflow=@demo_workflow.yaml" \
    -F "input_artifact=@demo_input.json" \
    http://localhost:8002/run-workflow/
  ```

### UI Features
- **OCR Demo:** Upload images, run OCR, view formatted results with line-by-line text display
- **Workflow Runner:** Upload YAML workflows, select adapters, provide JSON input, view results
- **Audit Logs:** All workflow steps, tool calls, and errors are logged and displayed
- **Error Handling:** Clear error messages for malformed workflows, missing files, and API failures

### Authentication (OCR)
- **Method:** Application Default Credentials (ADC)
- **Setup:**
  ```bash
  gcloud auth application-default login
  gcloud config set project <PROJECT_ID>
  gcloud auth application-default set-quota-project <PROJECT_ID>
  ```
- **Enable API:** Cloud Vision API must be enabled in your Google Cloud project
  ```bash
  gcloud services enable vision.googleapis.com
  ```

### Test
- See `tests/integration/test_api.py` for an automated test example.

### Implementation Notes
- The API uses the same engine and adapters as the CLI.
- Audit log is returned for transparency and debugging.
