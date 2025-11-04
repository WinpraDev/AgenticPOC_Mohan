#!/bin/bash
set -e

echo "🚀 Deploying script_20251104_153701..."

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
if docker ps | grep -q script_20251104_153701; then
    echo "✅ Container is running!"
    echo ""
    echo "Container: script_20251104_153701"
    echo "View logs: docker-compose logs -f"
    echo "Check results: ls -la results/"
    echo "Stop: docker-compose down"
else
    echo "❌ Container failed to start. Check logs:"
    echo "docker-compose logs"
    exit 1
fi
