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
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check (Cloud Run sets PORT automatically, default to 8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8080}/docs')" || exit 1

# Run via entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
