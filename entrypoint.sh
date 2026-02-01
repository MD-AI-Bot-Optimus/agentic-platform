#!/bin/bash
# Entrypoint script for Cloud Run
# Reads PORT environment variable and starts uvicorn

PORT=${PORT:-8080}
exec uvicorn src.agentic_platform.api:app --host 0.0.0.0 --port $PORT
