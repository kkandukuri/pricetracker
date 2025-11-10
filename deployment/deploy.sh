#!/bin/bash
# Price Tracker - Docker Deployment Script

set -e

echo "=========================================="
echo "Price Tracker - Docker Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Detect docker-compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Navigate to deployment directory
cd "$(dirname "$0")"

# Stop existing containers
echo "Stopping existing containers..."
$DOCKER_COMPOSE down

# Build Docker image
echo ""
echo "Building Docker image..."
$DOCKER_COMPOSE build --no-cache

# Start containers
echo ""
echo "Starting containers..."
$DOCKER_COMPOSE up -d

# Wait for service to be healthy
echo ""
echo "Waiting for service to be ready..."
sleep 10

# Check if service is running
if docker ps | grep -q pricetracker-app; then
    echo -e "${GREEN}✓ Price Tracker is running!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  - http://localhost:5000 (direct)"
    echo "  - http://localhost (via nginx)"
    echo ""
    echo "Check logs:"
    echo "  docker logs -f pricetracker-app"
    echo ""
    echo "Stop the application:"
    echo "  cd deployment && $DOCKER_COMPOSE down"
else
    echo -e "${RED}✗ Failed to start Price Tracker${NC}"
    echo "Check logs: docker logs pricetracker-app"
    exit 1
fi

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
