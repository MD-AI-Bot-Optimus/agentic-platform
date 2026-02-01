# Multi-stage build for efficiency
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY sample_data/ sample_data/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/docs')"

# Run the application
CMD ["uvicorn", "src.agentic_platform.api:app", "--host", "0.0.0.0", "--port", "8002"]
