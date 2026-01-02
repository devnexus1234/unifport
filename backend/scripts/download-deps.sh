#!/bin/bash
# Script to download all dependencies for offline Docker builds
# Run this on a machine with internet access

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
DEPS_DIR="$BACKEND_DIR/deps"

echo "Creating deps directory structure..."
mkdir -p "$DEPS_DIR/oracle-rpms"
mkdir -p "$DEPS_DIR/debian-packages"
mkdir -p "$DEPS_DIR/python-wheels"

cd "$DEPS_DIR"

echo ""
echo "=========================================="
echo "Downloading Oracle Instant Client RPMs..."
echo "=========================================="

# Oracle Instant Client Release RPM
ORACLE_RELEASE_RPM="oracle-instantclient-release-el8-1.0-1.x86_64.rpm"
if [ ! -f "oracle-rpms/$ORACLE_RELEASE_RPM" ]; then
    echo "Downloading oracle-instantclient-release-el8..."
    # Note: You need to accept Oracle license and download manually from:
    # https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html
    echo "ERROR: Oracle Instant Client requires manual download"
    echo "Please download the following from Oracle website (requires Oracle account):"
    echo "  1. oracle-instantclient-release-el8-1.0-1.x86_64.rpm"
    echo "  2. oracle-instantclient-basic-*.rpm (latest version)"
    echo ""
    echo "Place them in: $DEPS_DIR/oracle-rpms/"
    echo ""
    echo "Direct download links (after login):"
    echo "  Release RPM: https://yum.oracle.com/repo/OracleLinux/OL8/oracle/instantclient/x86_64/getPackage/oracle-instantclient-release-el8-1.0-1.x86_64.rpm"
    echo "  Basic RPM: Check Oracle Instant Client downloads page"
else
    echo "✓ $ORACLE_RELEASE_RPM already exists"
fi

echo ""
echo "=========================================="
echo "Downloading Debian packages..."
echo "=========================================="

# Create a temporary directory for downloading
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download Debian packages for python:3.11-slim (Debian Bookworm)
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

echo "Fetching package lists for Debian $DEBIAN_VERSION..."
apt-get download $(for pkg in "${PACKAGES[@]}"; do echo "$pkg:${ARCH}"; done) 2>/dev/null || {
    echo "Note: apt-get download requires root or proper configuration"
    echo "Alternative: Use 'apt download' with proper sources.list"
    echo ""
    echo "Manual download instructions:"
    echo "1. Configure /etc/apt/sources.list with Debian $DEBIAN_VERSION repositories"
    echo "2. Run: apt update"
    echo "3. For each package, run: apt download <package-name>"
    echo "4. Copy .deb files to: $DEPS_DIR/debian-packages/"
}

# Move downloaded packages
if ls *.deb 1> /dev/null 2>&1; then
    mv *.deb "$DEPS_DIR/debian-packages/"
    echo "✓ Debian packages downloaded to $DEPS_DIR/debian-packages/"
else
    echo "⚠ No .deb files found. Please download manually."
fi

cd "$DEPS_DIR"
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "Downloading Python wheels (optional)..."
echo "=========================================="
echo "Note: If using Nexus repository, Python packages will be installed from there"
echo "      during Docker build. This step is optional."
echo ""
echo "To download Python wheels manually:"
echo "  pip download -r $BACKEND_DIR/requirements.txt -d $DEPS_DIR/python-wheels"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Dependencies directory: $DEPS_DIR"
echo ""
echo "Oracle RPMs:"
ls -lh oracle-rpms/ 2>/dev/null || echo "  (empty - requires manual download)"
echo ""
echo "Debian packages:"
ls -lh debian-packages/ 2>/dev/null || echo "  (empty - requires manual download)"
echo ""
echo "Python wheels:"
ls -lh python-wheels/ 2>/dev/null || echo "  (empty - optional if using Nexus)"
echo ""
echo "Next steps:"
echo "1. Ensure all Oracle RPMs are in oracle-rpms/"
echo "2. Ensure all Debian packages are in debian-packages/"
echo "3. Copy deps/ folder to your offline RHEL server"
echo "4. Build using: docker build -f Dockerfile.offline -t unified-portal-backend ."
