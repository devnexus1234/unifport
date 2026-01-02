#!/bin/bash
# Script to fix SQLAlchemy Python 3.13 compatibility issue

set -e

cd /home/rohit/github/unified-portal/backend

echo "=== Fixing SQLAlchemy Python 3.13 compatibility ==="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run 'make setup' first."
    exit 1
fi

source venv/bin/activate

echo "Current SQLAlchemy version:"
pip show sqlalchemy | grep Version || echo "SQLAlchemy not installed"

echo ""
echo "Uninstalling old SQLAlchemy..."
pip uninstall -y sqlalchemy 2>/dev/null || true

echo ""
echo "Installing SQLAlchemy >= 2.0.31 (Python 3.13 compatible)..."
pip install 'sqlalchemy>=2.0.31'

echo ""
echo "New SQLAlchemy version:"
pip show sqlalchemy | grep Version

echo ""
echo "Testing SQLAlchemy import..."
python -c "from sqlalchemy import create_engine, text; print('✓ SQLAlchemy import successful')"

echo ""
echo "Testing database module import..."
python -c "from app.core.database import SessionLocal, get_engine, Base; print('✓ Database module import successful')"

echo ""
echo "=== Fix complete! ==="
echo "You can now run: make init-db"