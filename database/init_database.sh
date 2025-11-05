#!/bin/bash

# ============================================================
# DSCR POC Database Initialization Script
# ============================================================
# This script initializes the PostgreSQL database with Docker
# ============================================================

set -e

echo "=================================================="
echo "  DSCR POC Database Initialization"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "  Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Navigate to database directory
cd "$(dirname "$0")"

# Stop existing container if running
if docker ps -a | grep -q "dscr_poc_postgres"; then
    echo -e "${YELLOW}! Stopping existing container...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Existing container stopped${NC}"
    echo ""
fi

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Check if database is accessible
MAX_TRIES=30
COUNT=0
until docker exec dscr_poc_postgres pg_isready -U dscr_user -d dscr_poc_db > /dev/null 2>&1; do
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo -e "${RED}✗ Database failed to start after ${MAX_TRIES} seconds${NC}"
        exit 1
    fi
    echo "  Waiting for database... ($COUNT/$MAX_TRIES)"
    sleep 1
done

echo -e "${GREEN}✓ Database is ready${NC}"
echo ""

# Verify data
echo "Verifying database setup..."
PROPERTY_COUNT=$(docker exec dscr_poc_postgres psql -U dscr_user -d dscr_poc_db -t -c "SELECT COUNT(*) FROM properties" 2>/dev/null | tr -d ' ')
METRICS_COUNT=$(docker exec dscr_poc_postgres psql -U dscr_user -d dscr_poc_db -t -c "SELECT COUNT(*) FROM financial_metrics" 2>/dev/null | tr -d ' ')

echo -e "${GREEN}✓ Properties: ${PROPERTY_COUNT}${NC}"
echo -e "${GREEN}✓ Financial Metrics: ${METRICS_COUNT}${NC}"
echo ""

# Display connection info
echo "=================================================="
echo "  Database Ready!"
echo "=================================================="
echo ""
echo "Connection Details:"
echo "  Host:     localhost"
echo "  Port:     5433"
echo "  Database: dscr_poc_db"
echo "  User:     dscr_user"
echo "  Password: dscr_password_change_me"
echo ""
echo "Connection String:"
echo "  postgresql://dscr_user:dscr_password_change_me@localhost:5433/dscr_poc_db"
echo ""
echo "Docker Commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Connect:      docker exec -it dscr_poc_postgres psql -U dscr_user -d dscr_poc_db"
echo ""
echo "=================================================="

