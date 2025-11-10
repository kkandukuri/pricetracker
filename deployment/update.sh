#!/bin/bash
# Price Tracker - Update Script

set -e

echo "=========================================="
echo "Price Tracker - Update Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to project root
cd "$(dirname "$0")/.."

# Detect docker-compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "Step 1: Pulling latest code from repository..."
if [ -d ".git" ]; then
    git pull
    echo -e "${GREEN}✓ Code updated${NC}"
else
    echo -e "${YELLOW}⚠ Not a git repository. Skipping code update.${NC}"
fi

echo ""
echo "Step 2: Stopping containers..."
cd deployment
$DOCKER_COMPOSE down

echo ""
echo "Step 3: Rebuilding Docker image..."
$DOCKER_COMPOSE build --no-cache

echo ""
echo "Step 4: Starting updated containers..."
$DOCKER_COMPOSE up -d

echo ""
echo "Step 5: Cleaning up old Docker images..."
docker image prune -f

echo ""
echo "Step 6: Waiting for service to be ready..."
sleep 10

# Check if service is running
if docker ps | grep -q pricetracker-app; then
    echo -e "${GREEN}✓ Update successful!${NC}"
    echo ""
    echo "Application is running:"
    echo "  docker logs -f pricetracker-app"
else
    echo -e "${RED}✗ Update failed${NC}"
    echo "Check logs: docker logs pricetracker-app"
    exit 1
fi

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
