#!/bin/bash
# Script to install system dependencies and Python packages

set -e

echo "=== Installing system dependencies for python-ldap ==="
sudo apt-get update -qq
sudo apt-get install -y libldap2-dev libsasl2-dev

echo ""
echo "=== Installing Python dependencies ==="
cd /home/demo/github/unified-portal/backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Verifying installation ==="
python -c "import ldap; print('✓ python-ldap installed')" || echo "⚠ python-ldap not installed"
python -c "from pydantic_settings import BaseSettings; print('✓ pydantic-settings installed')" || echo "⚠ pydantic-settings not installed"

echo ""
echo "=== Installation complete ==="