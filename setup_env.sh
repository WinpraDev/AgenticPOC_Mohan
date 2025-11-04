#!/bin/bash
# Setup script for Meta-Agent project
# Creates .env file with correct database configuration from WinPrA Agentic POC

set -e

echo "=================================================="
echo "Meta-Agent Setup Script"
echo "=================================================="
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
fi

echo "Creating .env file..."

cat > .env << 'EOF'
# LM Studio Configuration (REQUIRED)
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-coder-7b-instruct-mlx
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096
LLM_CONTEXT_LENGTH=8192

# Database Configuration (REQUIRED)
# Using WinPrA Agentic POC database (DSCR POC)
DATABASE_URL=postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db

# Meta-Agent Configuration
META_AGENT_LOG_LEVEL=INFO
META_AGENT_MAX_RETRIES=3
META_AGENT_TIMEOUT=300
META_AGENT_STRICT_MODE=true

# Sandbox Configuration (for custom code execution)
DOCKER_TIMEOUT=30
SANDBOX_MEMORY_LIMIT=512m
SANDBOX_CPU_LIMIT=1.0
SANDBOX_IMAGE=python:3.11-slim

# Output Configuration
# Note: Agent Factory legacy fields removed - Meta-Agent uses generated_scripts/ instead
LOG_DIR=./logs
EOF

echo "✓ .env file created"
echo ""

# Check if Docker containers are running
echo "Checking DSCR POC database status..."
if docker ps | grep -q "dscr_poc_postgres"; then
    echo "✓ DSCR POC database is running"
else
    echo "⚠️  DSCR POC database is not running"
    echo ""
    echo "To start the database:"
    echo "  cd '/Users/mohan_cr/Desktop/WinPra/Codebase/WinPrA Agentic POC'"
    echo "  docker-compose up -d postgres"
    echo ""
fi

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Ensure LM Studio is running with qwen2.5-coder-7b-instruct-mlx"
echo "  2. Start DSCR POC database if not running (see above)"
echo "  3. Run: python test_setup.py"
echo "  4. Run: python simple_example.py"
echo ""

