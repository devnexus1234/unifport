#!/bin/bash
# Script to download Debian packages for offline use
# Run this on a Debian/Ubuntu machine with internet access

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
DEPS_DIR="$BACKEND_DIR/deps/debian-packages"

echo "Creating deps directory..."
mkdir -p "$DEPS_DIR"

cd "$DEPS_DIR"

# Debian version for python:3.11-slim (Debian Bookworm)
DEBIAN_VERSION="bookworm"
ARCH="amd64"

PACKAGES=(
    "gcc"
    "g++"
    "libldap2-dev"
    "libsasl2-dev"
    "libaio-dev"
    "libaio1"
)

echo "Downloading Debian packages for $DEBIAN_VERSION ($ARCH)..."
echo "Packages: ${PACKAGES[*]}"
echo ""

# Download packages and their dependencies
for pkg in "${PACKAGES[@]}"; do
    echo "Downloading $pkg..."
    apt-get download "$pkg:$ARCH" 2>/dev/null || \
    apt download "$pkg:$ARCH" 2>/dev/null || {
        echo "⚠ Failed to download $pkg"
        echo "  Make sure you have proper Debian $DEBIAN_VERSION sources configured"
        echo "  Run: sudo apt update"
    }
done

# Download dependencies
echo ""
echo "Downloading dependencies..."
apt-get download $(apt-cache depends --recurse --no-recommends --no-suggests \
    --no-conflicts --no-breaks --no-replaces --no-enhances \
    "${PACKAGES[@]}" | grep "^\w" | sort -u) 2>/dev/null || \
apt download $(apt-cache depends --recurse --no-recommends --no-suggests \
    --no-conflicts --no-breaks --no-replaces --no-enhances \
    "${PACKAGES[@]}" | grep "^\w" | sort -u) 2>/dev/null || {
    echo "⚠ Some dependencies may be missing"
}

echo ""
echo "=========================================="
echo "Download complete!"
echo "=========================================="
echo "Packages downloaded to: $DEPS_DIR"
echo ""
ls -lh "$DEPS_DIR"/*.deb 2>/dev/null | wc -l | xargs echo "Total .deb files:"
echo ""
echo "Next steps:"
echo "1. Copy the deps/ folder to your offline RHEL server"
echo "2. Build Docker image using Dockerfile.offline"
