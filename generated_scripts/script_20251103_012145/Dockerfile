FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY script.py .

# Create directories for outputs
RUN mkdir -p /app/results /app/logs /app/exports/reports /app/exports/data /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/app/results
ENV LOG_DIR=/app/logs

# Run the script
CMD ["python", "script.py"]
