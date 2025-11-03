FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all agents
COPY agents/ ./agents/

# Copy orchestrator and simulation runner
COPY orchestrator.py .
COPY run_simulation.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create directories for file storage
RUN mkdir -p logs results exports/reports exports/data data

# Expose ports (if needed for API)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command runs orchestrator
CMD ["python", "orchestrator.py"]
