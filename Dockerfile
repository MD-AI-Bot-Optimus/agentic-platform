# Multi-stage build for efficiency
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
    python-multipart>=0.0.6

# Copy application code
COPY src/ src/
COPY sample_data/ sample_data/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application - use shell form to expand PORT variable
# Cloud Run automatically sets PORT to 8080
CMD sh -c 'python -m uvicorn src.agentic_platform.api:app --host 0.0.0.0 --port ${PORT:-8080}'
