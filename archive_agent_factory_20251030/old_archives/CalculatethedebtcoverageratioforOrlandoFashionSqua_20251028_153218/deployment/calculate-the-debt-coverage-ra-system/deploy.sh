#!/bin/bash
set -e

echo "========================================================================"
echo "Deploying Calculate The Debt Coverage Ra System (Single Container)"
echo "========================================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment
source .env

# Create necessary directories on host
echo "Creating directories for file storage..."
mkdir -p logs results exports/reports exports/data data

echo ""
echo "Directory Structure:"
echo "  logs/           - System logs"
echo "  results/        - Analysis results (JSON)"
echo "  exports/        - Generated reports and files"
echo "    ├── reports/  - PDF, Excel reports"
echo "    └── data/     - Exported data files"
echo "  data/           - Input data files"
echo ""

echo "Building Docker image..."
docker-compose build

echo "Starting container..."
docker-compose up -d

echo ""
echo "========================================================================"
echo "✓ Calculate The Debt Coverage Ra System deployed successfully!"
echo "========================================================================"
echo ""
echo "Container status:"
docker-compose ps

echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Run single analysis:"
echo "  docker exec calculate-the-debt-coverage-ra-system python orchestrator.py"
echo ""
echo "Run simulations:"
echo "  docker exec calculate-the-debt-coverage-ra-system python run_simulation.py scenario"
echo ""
echo "Run batch analysis:"
echo "  docker exec calculate-the-debt-coverage-ra-system python run_simulation.py batch"
echo ""
echo "Stop system:"
echo "  docker-compose down"
echo "========================================================================"
