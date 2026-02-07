# Multi-stage build for efficiency
# Stage 1: Build React UI
FROM node:18-alpine AS ui-builder
WORKDIR /ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

# Stage 2: Build Python API
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    google-cloud-vision>=3.0.0 \
    requests>=2.31.0 \
    pyyaml>=6.0 \
    python-multipart>=0.0.6 \
    jsonschema>=4.0.0 \
    httpx>=0.24.0 \
    langchain>=0.1.0 \
    langchain-core>=0.1.0 \
    langchain-anthropic>=0.1.0 \
    langchain-openai>=0.1.0 \
    langchain-google-vertexai>=0.1.0 \
    python-dotenv>=1.0.0 \
    pydantic>=2.0.0

# Copy application code
COPY src/ src/
COPY sample_data/ sample_data/


# Copy built UI from first stage
COPY --from=ui-builder /ui/dist ui/dist

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Test that imports work
RUN python -c "import sys; sys.path.insert(0, '/app/src'); from agentic_platform.api import app; print('✓ App imports successfully')"

# Run the application - use shell form to expand PORT variable
# Cloud Run automatically sets PORT to 8080
CMD sh -c 'python -m uvicorn src.agentic_platform.api:app --host 0.0.0.0 --port ${PORT:-8080}'
