#!/bin/bash
# Force rebuild Docker image to fix libaio issue
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "Rebuilding Docker Backend Image"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

echo "Stopping existing containers..."
docker-compose down backend 2>/dev/null || true

echo "Removing old backend image..."
docker rmi unified-portal-backend 2>/dev/null || \
docker rmi $(docker images | grep -E "backend|unified-portal" | awk '{print $3}') 2>/dev/null || true

echo ""
echo "Building backend image with --no-cache..."
docker-compose build --no-cache backend

echo ""
echo "=========================================="
echo "Testing Oracle Client"
echo "=========================================="
echo ""

echo "Running test in container..."
docker-compose run --rm --no-deps backend python -c "import cx_Oracle; print('✓ Oracle client working!')" || {
    echo ""
    echo "Running detailed test..."
    docker-compose run --rm --no-deps backend /app/scripts/test-oracle-client.sh || true
}

echo ""
echo "=========================================="
echo "Rebuild complete!"
echo "=========================================="
echo ""
echo "You can now run: make dev-with-db ENV=development"
