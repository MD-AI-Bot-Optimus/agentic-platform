"""
FastAPI application for Agentic Platform with OCR and workflow execution endpoints.

Provides:
- POST /run-ocr/ : Extract text from images using Google Vision API
- POST /run-workflow/ : Execute YAML-defined workflows with pluggable adapters
- POST /mcp/request : Handle MCP (Model Context Protocol) requests
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from agentic_platform.audit.audit_log import InMemoryAuditLog
from agentic_platform.tools.tool_registry import ToolRegistry
from agentic_platform.adapters.mcp_server import MCPServer
# from agentic_platform.adapters.mcp_adapter import MCPAdapter
# from agentic_platform.adapters.langgraph_adapter import LangGraphAdapter
from agentic_platform.workflow import engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Platform API",
    description="REST API for OCR, workflow execution, and MCP protocol",
    version="0.1.0"
)

# Initialize global tool registry and MCP server
tool_registry = ToolRegistry()
mcp_server = MCPServer(tool_registry, version="0.1.0")

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Serve UI or return API welcome message."""
    ui_dist_path = Path(__file__).parent.parent.parent / "ui" / "dist"
    ui_index_path = ui_dist_path / "index.html"
    if ui_index_path.exists():
        return FileResponse(ui_index_path, media_type="text/html")
    
    # Fallback to JSON response if UI not available
    return {
        "message": "🤖 Agentic Platform API",
        "version": "0.1.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "ocr": "/run-ocr",
            "workflow": "/run-workflow/",
            "mcp_tools": "/mcp/tools",
            "mcp_request": "/mcp/request"
        },
        "docs_url": "https://agentic-platform-api-7erqohmwxa-uc.a.run.app/docs"
    }


@app.get("/demo_workflow.yaml")
async def get_demo_workflow():
    """Serve demo workflow YAML file."""
    demo_path = Path(__file__).parent.parent.parent / "demo_workflow.yaml"
    if demo_path.exists():
        return FileResponse(demo_path, media_type="application/x-yaml", filename="demo_workflow.yaml")
    raise HTTPException(status_code=404, detail="Demo workflow file not found")


@app.get("/demo_input.json")
async def get_demo_input():
    """Serve demo input JSON file."""
    demo_path = Path(__file__).parent.parent.parent / "demo_input.json"
    if demo_path.exists():
        return FileResponse(demo_path, media_type="application/json", filename="demo_input.json")
    raise HTTPException(status_code=404, detail="Demo input file not found")


@app.get("/sample_data/{file_path:path}")
async def get_sample_data(file_path: str):
    """Serve sample data files (images, etc.)."""
    sample_file = Path(__file__).parent.parent.parent / "sample_data" / file_path
    
    # Security check: prevent directory traversal
    try:
        sample_file = sample_file.resolve()
        sample_dir = (Path(__file__).parent.parent.parent / "sample_data").resolve()
        if not str(sample_file).startswith(str(sample_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if sample_file.exists() and sample_file.is_file():
        return FileResponse(sample_file)
    raise HTTPException(status_code=404, detail="Sample file not found")


@app.post("/run-ocr/")
async def run_ocr_workflow(
    request: Request,
    file_path: Optional[str] = Form(None)
) -> JSONResponse:
    """
    Execute OCR on an uploaded image using Google Vision API.

    Args:
        request: The FastAPI request object
        file_path: Path to image file on server (for sample files)

    Returns:
        JSON response with OCR result, tool results, and audit log

    Raises:
        HTTPException: If workflow execution fails
    """
    try:
        # Parse form data manually
        form = await request.form()
        image = form.get("image")
        credentials_json = form.get("credentials_json")
        
        if file_path:
            # Use provided file path (for sample files)
            # Convert relative path to absolute path relative to project root
            if not os.path.isabs(file_path):
                # Assume file_path is relative to project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                img_path = os.path.join(project_root, file_path)
            else:
                img_path = file_path
            creds_path = None
        else:
            # Handle uploaded image
            if not image:
                raise HTTPException(status_code=400, detail="Either image file or file_path must be provided")
            
            # Save uploaded image to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as img_tmp:
                img_bytes = await image.read()
                img_tmp.write(img_bytes)
                img_path = img_tmp.name

            creds_path = None
            if credentials_json:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as creds_tmp:
                    creds_bytes = await credentials_json.read()
                    creds_tmp.write(creds_bytes)
                    creds_path = creds_tmp.name

        # Load OCR workflow
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "workflows/ocr_mvp.yaml"
        )
        with open(workflow_path, "r") as wf_file:
            wf_def = yaml.safe_load(wf_file)

        # Prepare workflow input - wrap in "inputs" to match YAML template references
        input_data = {
            "inputs": {
                "image_path": img_path,
                "credentials_json": creds_path or ""
            }
        }

        # Execute workflow
        audit_log = InMemoryAuditLog()
        tool_client = ToolRegistry()
        result = engine.run(
            wf_def,
            input_artifact=input_data,
            tool_client=tool_client,
            audit_log=audit_log
        )

        # Format results
        job_id = result.get("job_id", "job-1")
        audit_events = [vars(e) for e in audit_log.get_events(job_id)]
        tool_results = result.get("tool_results", [])

        formatted_lines = []
        ocr_error = None
        if tool_results:
            first_res = tool_results[0].get("result", {})
            text = first_res.get("text", "")
            ocr_error = first_res.get("error")
            if text:
                formatted_lines = text.splitlines()

        logger.info(f"OCR workflow completed successfully for image: {image.filename if image else 'sample file'}")
        return JSONResponse({
            "result": result,
            "tool_results": tool_results,
            "audit_log": audit_events,
            "formatted_text_lines": formatted_lines,
            "error": ocr_error
        })

    except Exception as e:
        logger.error(f"OCR workflow execution error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail=f"OCR workflow execution error: {str(e)}"
        )
    finally:
        # Clean up temporary files
        if os.path.exists(img_path):
            os.remove(img_path)
        if creds_path and os.path.exists(creds_path):
            os.remove(creds_path)


@app.post("/run-workflow/")
async def run_workflow(
    workflow: UploadFile = File(..., description="YAML workflow definition file"),
    input_artifact: UploadFile = File(..., description="JSON input artifact for the workflow"),
    adapter: Optional[str] = Form("mcp", description="Tool adapter to use (mcp or langgraph)")
) -> JSONResponse:
    """
    Execute a workflow defined in YAML with a JSON input artifact.

    **Parameters:**
    - **workflow**: YAML file with workflow definition (required). Must have `nodes` and `edges` keys.
    - **input_artifact**: JSON file with input data for the workflow (required)
    - **adapter**: Tool adapter to use - 'mcp' or 'langgraph' (optional, defaults to 'mcp')

    **Workflow YAML Format:**
    ```yaml
    nodes:
      - id: start
        type: start
      - id: step_name
        type: tool
        tool: tool_name
        args:
          arg1: value1
      - id: end
        type: end
    edges:
      - from: start
        to: step_name
      - from: step_name
        to: end
    ```

    **Returns:**
    - `result`: Workflow execution result with job_id, status, and tool_results
    - `tool_results`: Array of tool execution results
    - `audit_log`: Audit trail of all events

    **Raises:**
    - 400: If workflow YAML or input JSON is malformed
    - 422: If workflow execution fails
    """
    # Validate file uploads
    if not workflow:
        raise HTTPException(status_code=422, detail="workflow file is required")
    if not input_artifact:
        raise HTTPException(status_code=422, detail="input_artifact file is required")
    
    # Parse workflow YAML
    try:
        workflow_content = await workflow.read()
        if not workflow_content:
            raise ValueError("Workflow file is empty")
        # Decode bytes to string if needed
        if isinstance(workflow_content, bytes):
            workflow_text = workflow_content.decode('utf-8')
        else:
            workflow_text = workflow_content
        logger.debug(f"Workflow content (first 200 chars): {workflow_text[:200]}")
        wf_def = yaml.safe_load(workflow_text)
        if not wf_def:
            raise ValueError("Workflow YAML is empty or parses to None")
        if not isinstance(wf_def, dict):
            raise ValueError(f"Workflow must be a YAML object/dict, got {type(wf_def).__name__}")
        if "nodes" not in wf_def or "edges" not in wf_def:
            raise ValueError(f"Workflow must contain 'nodes' and 'edges' keys. Found keys: {list(wf_def.keys())}")
    except Exception as e:
        logger.error(f"Malformed workflow YAML: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed workflow YAML: {str(e)}"
        )

    # Parse input JSON
    try:
        input_content = await input_artifact.read()
        if not input_content:
            input_data = {}
        else:
            input_data = json.loads(input_content.decode())
    except Exception as e:
        logger.error(f"Malformed input JSON: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed input JSON: {str(e)}"
        )

    # Select adapter
    tool_client = tool_registry

    try:
        audit_log = InMemoryAuditLog()
        result = engine.run(
            wf_def,
            input_artifact=input_data,
            tool_client=tool_client,
            audit_log=audit_log
        )
        job_id = result.get("job_id", "job-1")
        audit_events = [vars(e) for e in audit_log.get_events(job_id)]
        logger.info(f"Workflow executed successfully with adapter: {adapter}")
        return JSONResponse({
            "result": result,
            "tool_results": result.get("tool_results", []),
            "audit_log": audit_events
        })
    except Exception as e:
        logger.error(f"Workflow execution error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail=f"Workflow execution error: {str(e)}"
        )


# ============================================================================
# MCP (Model Context Protocol) Endpoints
# ============================================================================

@app.post("/mcp/request")
async def handle_mcp_request(request: Dict[str, Any]) -> JSONResponse:
    """
    Handle MCP (Model Context Protocol) JSON-RPC 2.0 requests.

    Supports the following methods:
    - initialize: Handshake and capability negotiation
    - tools/list: Discover available tools
    - tools/call: Execute a tool

    Args:
        request: JSON-RPC 2.0 request object

    Returns:
        JSON-RPC 2.0 response (success or error)

    Example:
        POST /mcp/request
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
    """
    try:
        logger.debug(f"MCP request received: {request.get('method')}")

        # Handle the MCP request via server
        response = mcp_server.handle_request(request)

        logger.debug(f"MCP response: {response.get('result') or response.get('error')}")
        return JSONResponse(response)

    except Exception as e:
        logger.error("MCP request handling error", exc_info=True)
        # Return MCP error response
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": {"details": str(e)}
            },
            "id": request.get("id")
        }
        return JSONResponse(error_response, status_code=500)


@app.post("/mcp/call-tool")
async def call_mcp_tool(request: Dict[str, Any]) -> JSONResponse:
    """
    Call an MCP tool using REST-style API (non-MCP protocol).

    This is a convenience endpoint for calling tools without MCP JSON-RPC overhead.

    Args:
        request: JSON object with tool_name and arguments

    Returns:
        JSON response with tool result

    Example:
        POST /mcp/call-tool
        {
            "tool_name": "google_vision_ocr",
            "arguments": {"image_path": "path/to/image.jpg"}
        }
    """
    try:
        tool_name = request.get("tool_name")
        arguments = request.get("arguments", {})

        if not tool_name:
            return JSONResponse({
                "error": "Missing tool_name",
                "message": "tool_name is required"
            }, status_code=400)

        logger.debug(f"MCP tool call: {tool_name} with args: {arguments}")

        # Get tool from registry
        tool_spec = tool_registry.get_tool(tool_name)
        if not tool_spec:
            return JSONResponse({
                "error": "Tool not found",
                "message": f"Tool '{tool_name}' not found"
            }, status_code=404)

        # Call the tool
        result = tool_spec.handler(arguments)

        logger.debug(f"MCP tool result: {result}")
        return JSONResponse({
            "tool_name": tool_name,
            "result": result
        })

    except Exception as e:
        logger.error(f"MCP tool call error: {str(e)}", exc_info=True)
        return JSONResponse({
            "error": "Tool execution failed",
            "message": str(e)
        }, status_code=500)


@app.get("/mcp/tools")
async def list_mcp_tools() -> JSONResponse:
    """
    Get list of available tools in a simplified format (non-MCP).

    Returns:
        JSON array of tools with name, description, and inputSchema

    This endpoint is useful for UI discovery without MCP protocol overhead.
    """
    try:
        tool_names = tool_registry.list_tools()
        tools = []

        for name in tool_names:
            tool_spec = tool_registry.get_tool(name)
            if tool_spec:
                tools.append({
                    "name": name,
                    "description": tool_spec.description,
                    "inputSchema": tool_spec.schema
                })

        logger.debug(f"Listed {len(tools)} tools")
        return JSONResponse({"tools": tools})

    except Exception as e:
        logger.error("Error listing tools", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tools: {str(e)}"
        )


@app.post("/agent/execute")
async def execute_agent(prompt: str = Form(...), model: str = Form("mock-llm")):
    """
    Execute LangGraph agent with a prompt.
    
    Demonstrates autonomous reasoning with tool orchestration.
    
    Query parameters:
    - prompt: User query for the agent
    - model: LLM model to use (default: mock-llm for cost-free demo)
             Options: mock-llm, claude-3.5-sonnet, gpt-4-turbo, gemini-1.5-pro
    
    Returns:
    - status: success/incomplete/error
    - final_output: Agent's response
    - reasoning_steps: List of reasoning steps
    - iterations: Number of iterations
    - tool_calls: Tools executed
    """
    try:
        from agentic_platform.adapters.langgraph_agent import LangGraphAgent
        from agentic_platform.llm import get_llm_model, validate_llm_setup
        
        logger.info(f"Agent execution request: model={model}, prompt length={len(prompt)}")
        
        # Validate LLM setup
        setup_status = validate_llm_setup()
        logger.debug(f"LLM setup status: {setup_status}")
        
        # Get the appropriate LLM based on model parameter
        try:
            llm = get_llm_model(model=model)
            logger.info(f"Initialized LLM: {model}")
        except ValueError as e:
            logger.warning(f"Could not initialize real LLM ({model}): {str(e)}, falling back to mock LLM")
            from agentic_platform.llm.mock_llm import MockLLM
            llm = MockLLM(model=model)
        
        # Initialize agent with the selected LLM
        agent = LangGraphAgent(
            model=model,
            llm=llm,
            max_iterations=3
        )
        
        # Execute agent
        result = agent.execute(prompt)
        
        logger.info(f"Agent execution complete: status={result.status}, iterations={result.iterations}")
        
        # Convert LLMProvider enum to string for JSON serialization
        api_keys_status = {k: v for k, v in setup_status["api_keys_configured"].items()}
        
        return JSONResponse({
            "status": result.status,
            "final_output": result.final_output,
            "reasoning_steps": result.reasoning_steps,
            "iterations": result.iterations,
            "tool_calls": result.tool_calls,
            "error": result.error,
            "model_used": model,
            "llm_setup": {
                "use_mock_llm": setup_status["use_mock_llm"],
                "api_keys_configured": api_keys_status,
                "default_model": setup_status["default_model"][1],  # Get model name from tuple
                "available_models": setup_status["available_models"]
            }
        })
        
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )


@app.get("/agent/models")
async def list_agent_models():
    """
    List available LLM models for agent.
    
    Returns:
    - available_models: Dict mapping providers to model lists
    - api_keys_configured: Dict showing which providers have API keys
    """
    try:
        from agentic_platform.llm import list_available_models, LLMConfig
        
        models = list_available_models()
        keys_status = LLMConfig.validate_api_keys()
        
        logger.info("Listing available agent models")
        
        return JSONResponse({
            "available_models": models,
            "api_keys_configured": keys_status,
            "default_model": LLMConfig.get_default_model()[1]
        })
        
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        )


# Mount static UI files at /static (MUST be after all API routes)
# This serves /static/assets/*, /static/ui/
ui_dist_path = Path(__file__).parent.parent.parent / "ui" / "dist"
if ui_dist_path.exists():
    app.mount("/static", StaticFiles(directory=ui_dist_path, html=False), name="static")

    # Add catch-all route for SPA routing (must be after static files mount)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve SPA for any unmatched routes."""
        ui_index_path = ui_dist_path / "index.html"
        if ui_index_path.exists():
            return FileResponse(ui_index_path, media_type="text/html")
        
        # Fallback
        return {"detail": "Not Found"}
