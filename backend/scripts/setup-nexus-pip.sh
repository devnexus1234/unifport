#!/bin/bash
# Script to configure pip to use Nexus repository
# Run this before building the Docker image on RHEL server

set -e

NEXUS_URL="${NEXUS_URL:-http://nexus.example.com:8081/repository/pypi-group/simple}"
NEXUS_USER="${NEXUS_USER:-}"
NEXUS_PASSWORD="${NEXUS_PASSWORD:-}"

if [ -z "$NEXUS_URL" ]; then
    echo "ERROR: NEXUS_URL environment variable is required"
    echo "Usage: NEXUS_URL=http://your-nexus:8081/repository/pypi-group/simple ./setup-nexus-pip.sh"
    exit 1
fi

echo "Configuring pip to use Nexus repository: $NEXUS_URL"

# Create pip configuration directory
mkdir -p ~/.pip

# Create pip.conf
cat > ~/.pip/pip.conf <<EOF
[global]
index-url = $NEXUS_URL
trusted-host = $(echo $NEXUS_URL | sed -E 's|https?://([^:/]+).*|\1|')
EOF

# If credentials are provided, add them
if [ -n "$NEXUS_USER" ] && [ -n "$NEXUS_PASSWORD" ]; then
    # Encode credentials in URL format
    NEXUS_URL_WITH_AUTH=$(echo "$NEXUS_URL" | sed "s|://|://${NEXUS_USER}:${NEXUS_PASSWORD}@|")
    cat > ~/.pip/pip.conf <<EOF
[global]
index-url = $NEXUS_URL_WITH_AUTH
trusted-host = $(echo $NEXUS_URL | sed -E 's|https?://([^:/]+).*|\1|')
EOF
    echo "✓ Added authentication credentials"
fi

echo "✓ Pip configuration created at ~/.pip/pip.conf"
echo ""
echo "To use in Docker build, set environment variable:"
echo "  PIP_INDEX_URL=$NEXUS_URL"
echo ""
echo "Or mount pip.conf in Dockerfile:"
echo "  COPY pip.conf /root/.pip/pip.conf"
