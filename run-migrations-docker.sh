#!/bin/bash
# Script to run migrations and init-db in Docker container

set -e

echo "Building backend Docker image (this may take a few minutes)..."
docker-compose build backend

echo ""
echo "Running database migrations..."
docker-compose run --rm --no-deps \
  -e DATABASE_URL="oracle+cx_oracle://umduser:umd123@oracle:1521/XEPDB1" \
  -e ORACLE_HOST=oracle \
  -e ORACLE_USER=umduser \
  -e ORACLE_PASSWORD=umd123 \
  -e ORACLE_PORT=1521 \
  -e ORACLE_SERVICE=XEPDB1 \
  -e ENVIRONMENT=development \
  backend bash -c "cd /app && alembic upgrade head"

echo ""
echo "Initializing database with default data..."
docker-compose run --rm --no-deps \
  -e DATABASE_URL="oracle+cx_oracle://umduser:umd123@oracle:1521/XEPDB1" \
  -e ORACLE_HOST=oracle \
  -e ORACLE_USER=umduser \
  -e ORACLE_PASSWORD=umd123 \
  -e ORACLE_PORT=1521 \
  -e ORACLE_SERVICE=XEPDB1 \
  -e ENVIRONMENT=development \
  backend bash -c "cd /app && python scripts/init_db.py"

echo ""
echo "✓ Migrations and database initialization complete!"

