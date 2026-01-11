#!/bin/bash

# Celery worker startup script
# Runs the AI generation worker queue with proper configuration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Starting Celery AI Generation Worker"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}✗ Error: .env file not found!${NC}"
    echo ""
    echo "Please create .env file from .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then set your ANTHROPIC_API_KEY in .env"
    exit 1
fi

echo -e "${GREEN}✓ Found .env file${NC}"

# Check if ANTHROPIC_API_KEY is set in .env
if ! grep -q "^ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠ Warning: ANTHROPIC_API_KEY not properly set in .env${NC}"
    echo "  Make sure to set: ANTHROPIC_API_KEY=sk-ant-api03-..."
    echo ""
fi

# Load environment variables from .env
set -a
source .env
set +a

echo -e "${GREEN}✓ Loaded environment variables${NC}"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Redis is not running!${NC}"
    echo ""
    echo "Please start Redis:"
    echo "  macOS: brew services start redis"
    echo "  Linux: sudo systemctl start redis"
    exit 1
fi

echo -e "${GREEN}✓ Redis is running${NC}"

# Check if virtual environment is activated (optional)
if [ -z "$VIRTUAL_ENV" ] && [ ! -f "uv.lock" ]; then
    echo -e "${YELLOW}⚠ Warning: No virtual environment detected${NC}"
fi

echo ""
echo "Starting Celery worker..."
echo "  Queue: ai_generation"
echo "  Concurrency: 2"
echo "  Pool: solo (for async tasks)"
echo ""

# Start Celery worker
CELERY_WORKER=true PYTHONPATH=app exec uv run celery \
    -A workers.celery_app \
    worker \
    --loglevel=info \
    --queues=ai_generation \
    --concurrency=2 \
    --pool=solo \
    --max-tasks-per-child=1000
