#!/bin/bash
set -e

cd /home/demo/github/unified-portal

echo "=== Step 1: Starting Oracle Database ==="
make oracle-start 2>&1

echo ""
echo "=== Waiting a bit for Oracle to fully initialize ==="
sleep 5

echo ""
echo "=== Step 2: Running Database Migrations ==="
# Try local migration first, fallback to docker migration
if [ -d "backend/venv" ]; then
    echo "Using local virtual environment..."
    cd backend
    source venv/bin/activate
    export DATABASE_URL="oracle+cx_oracle://umd:umd123@localhost:1521/XEPDB1"
    export ORACLE_USER=umd
    export ORACLE_PASSWORD=umd123
    export ORACLE_HOST=localhost
    export ORACLE_PORT=1521
    export ORACLE_SERVICE=XEPDB1
    export ENVIRONMENT=development
    alembic upgrade head 2>&1
    cd ..
else
    echo "Virtual environment not found, using Docker migration..."
    make migrate-docker 2>&1
fi

echo ""
echo "=== Setup Complete ==="