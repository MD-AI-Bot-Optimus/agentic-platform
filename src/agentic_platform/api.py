"""
FastAPI application for Agentic Platform with OCR and workflow execution endpoints.

Provides:
- POST /run-ocr/ : Extract text from images using Google Vision API
- POST /run-workflow/ : Execute YAML-defined workflows with pluggable adapters
"""

import json
import logging
import os
import tempfile
from typing import Optional

import yaml
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agentic_platform.audit.audit_log import InMemoryAuditLog
from agentic_platform.tools.tool_registry import ToolRegistry
from agentic_platform.adapters.mcp_adapter import MCPAdapter
from agentic_platform.adapters.langgraph_adapter import LangGraphAdapter
from agentic_platform.workflow import engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Platform API",
    description="REST API for OCR and workflow execution",
    version="0.1.0"
)

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run-ocr/")
async def run_ocr_workflow(
    image: UploadFile = File(...),
    credentials_json: Optional[UploadFile] = File(None)
) -> JSONResponse:
    """
    Execute OCR on an uploaded image using Google Vision API.

    Args:
        image: Image file (JPEG, PNG, etc.)
        credentials_json: Optional Google credentials JSON file

    Returns:
        JSON response with OCR result, tool results, and audit log

    Raises:
        HTTPException: If workflow execution fails
    """
    # Save uploaded image to a temp file
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(image.filename)[-1]
    ) as img_tmp:
        img_bytes = await image.read()
        img_tmp.write(img_bytes)
        img_path = img_tmp.name

    creds_path = None
    if credentials_json:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as creds_tmp:
            creds_bytes = await credentials_json.read()
            creds_tmp.write(creds_bytes)
            creds_path = creds_tmp.name

    try:
        # Load OCR workflow
        workflow_path = os.path.join(
            os.path.dirname(__file__), "../workflows/ocr_mvp.yaml"
        )
        with open(workflow_path, "r") as wf_file:
            wf_def = yaml.safe_load(wf_file)

        # Prepare workflow input
        input_data = {
            "image_path": img_path,
            "credentials_json": creds_path or ""
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
        audit_events = [vars(e) for e in audit_log.get_events("job-1")]
        tool_results = result.get("tool_results", [])

        # Add formatted text lines for better UI display
        if (tool_results and
            "result" in tool_results[0] and
            "text" in tool_results[0]["result"]):
            text = tool_results[0]["result"]["text"]
            tool_results[0]["result"]["formatted_text_lines"] = text.splitlines()

        logger.info(f"OCR workflow completed successfully for image: {image.filename}")
        return JSONResponse({
            "result": result,
            "tool_results": tool_results,
            "audit_log": audit_events
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
    workflow: UploadFile = File(...),
    input_artifact: UploadFile = File(...),
    adapter: str = Form("mcp")
) -> JSONResponse:
    """
    Execute a workflow defined in YAML with a JSON input artifact.

    Args:
        workflow: YAML workflow definition file
        input_artifact: JSON input artifact for the workflow
        adapter: Tool adapter to use ('mcp' or 'langgraph', default: 'mcp')

    Returns:
        JSON response with workflow result, tool results, and audit log

    Raises:
        HTTPException: If workflow definition is malformed or execution fails
    """
    try:
        wf_def = yaml.safe_load(await workflow.read())
    except Exception as e:
        logger.error(f"Malformed workflow YAML: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed workflow YAML: {str(e)}"
        )

    try:
        input_data = json.loads((await input_artifact.read()).decode())
    except Exception as e:
        logger.error(f"Malformed input JSON: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Malformed input JSON: {str(e)}"
        )

    # Select adapter
    if adapter == "langgraph":
        tool_client = LangGraphAdapter()
    elif adapter == "mcp":
        tool_client = MCPAdapter()
    else:
        logger.error(f"Invalid adapter: {adapter}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid adapter: {adapter}"
        )

    try:
        audit_log = InMemoryAuditLog()
        result = engine.run(
            wf_def,
            input_artifact=input_data,
            tool_client=tool_client,
            audit_log=audit_log
        )
        audit_events = [vars(e) for e in audit_log.get_events("job-1")]
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

