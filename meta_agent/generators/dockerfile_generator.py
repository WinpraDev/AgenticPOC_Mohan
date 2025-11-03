"""
Dockerfile Generator
Generates Dockerfiles for script execution
"""

from typing import Dict, Any
from loguru import logger


def generate_dockerfile(
    script_name: str,
    requirements: str,
    has_web_interface: bool = False,
    port: int = 8080
) -> str:
    """
    Generate Dockerfile for script execution
    
    Args:
        script_name: Name of the script file
        requirements: Content of requirements.txt
        has_web_interface: Whether script has web interface
        port: Port to expose if web interface
        
    Returns:
        Dockerfile content as string
    """
    logger.debug("Generating Dockerfile...")
    
    dockerfile = f"""FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY {script_name} .

# Create directories for outputs
RUN mkdir -p /app/results /app/logs /app/exports/reports /app/exports/data /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/app/results
ENV LOG_DIR=/app/logs

"""
    
    # Add port exposure for web interface
    if has_web_interface:
        dockerfile += f"""# Expose web server port
EXPOSE {port}

"""
    
    # Add healthcheck for web interface
    if has_web_interface:
        dockerfile += f"""# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

"""
    
    # Add run command
    dockerfile += f"""# Run the script
CMD ["python", "{script_name}"]
"""
    
    logger.debug("✓ Dockerfile generated")
    return dockerfile


def generate_docker_compose(
    container_name: str,
    script_name: str,
    has_web_interface: bool = False,
    port: int = 8080,
    memory_limit: str = "512m",
    cpu_limit: float = 0.5
) -> str:
    """
    Generate docker-compose.yml
    
    Args:
        container_name: Name for the container
        script_name: Name of the script
        has_web_interface: Whether to map ports
        port: Port to map
        memory_limit: Memory limit (e.g., "512m", "1g")
        cpu_limit: CPU cores limit
        
    Returns:
        docker-compose.yml content
    """
    logger.debug("Generating docker-compose.yml...")
    
    # Start with base configuration
    compose = f"""version: '3.8'

services:
  {container_name}:
    build: .
    container_name: {container_name}
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - OUTPUT_DIR=/app/results
      - LOG_DIR=/app/logs
"""
    
    # Add port mapping for web interface
    if has_web_interface:
        compose += f"""      - PORT={port}
      - HOST=0.0.0.0
    ports:
      - "{port}:{port}"
"""
    
    # Add volume mounts
    compose += """    volumes:
      - ./results:/app/results:rw
      - ./logs:/app/logs:rw
      - ./exports/reports:/app/exports/reports:rw
      - ./exports/data:/app/exports/data:rw
      - ./data:/app/data:rw
"""
    
    # Add resource limits
    compose += f"""    mem_limit: {memory_limit}
    cpus: {cpu_limit}
"""
    
    # Add restart policy (no restart for task execution, unless web interface)
    if has_web_interface:
        compose += """    restart: unless-stopped
"""
    else:
        compose += """    restart: no
"""
    
    # Add network
    compose += """    networks:
      - script-network

networks:
  script-network:
    driver: bridge
"""
    
    logger.debug("✓ docker-compose.yml generated")
    return compose


def generate_deploy_script(container_name: str, has_web_interface: bool = False, port: int = 8080) -> str:
    """
    Generate deployment script
    
    Args:
        container_name: Container name
        has_web_interface: Whether container has web interface
        port: Web server port
        
    Returns:
        Bash deployment script
    """
    logger.debug("Generating deploy.sh...")
    
    script = f"""#!/bin/bash
set -e

echo "🚀 Deploying {container_name}..."

# Create required directories
mkdir -p logs results exports/reports exports/data data

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Please edit .env with your configuration"
        exit 1
    else
        echo "❌ No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Build the container
echo "🔨 Building container..."
docker-compose build

# Stop any existing container
echo "🛑 Stopping existing container (if any)..."
docker-compose down 2>/dev/null || true

# Start the container
echo "▶️  Starting container..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
sleep 3

# Check if container is running
if docker ps | grep -q {container_name}; then
    echo "✅ Container is running!"
    echo ""
    echo "Container: {container_name}"
"""
    
    if has_web_interface:
        script += f"""    echo "Web Interface: http://localhost:{port}"
    echo "Logs: docker-compose logs -f"
    echo "Stop: docker-compose down"
"""
    else:
        script += """    echo "View logs: docker-compose logs -f"
    echo "Check results: ls -la results/"
    echo "Stop: docker-compose down"
"""
    
    script += """else
    echo "❌ Container failed to start. Check logs:"
    echo "docker-compose logs"
    exit 1
fi
"""
    
    logger.debug("✓ deploy.sh generated")
    return script

