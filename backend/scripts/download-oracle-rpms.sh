#!/bin/bash
# Script to download Oracle Instant Client RPMs
# Note: This requires manual download from Oracle website due to license restrictions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
DEPS_DIR="$BACKEND_DIR/deps/oracle-rpms"

echo "=========================================="
echo "Oracle Instant Client RPM Download Guide"
echo "=========================================="
echo ""
echo "Oracle Instant Client requires manual download from Oracle website."
echo "This script provides instructions and verifies downloaded files."
echo ""

mkdir -p "$DEPS_DIR"

echo "Required RPMs:"
echo "  1. oracle-instantclient-release-el8-1.0-1.x86_64.rpm"
echo "  2. oracle-instantclient-basic-*.x86_64.rpm (latest version)"
echo ""

echo "Download Steps:"
echo "  1. Visit: https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html"
echo "  2. Accept the license agreement"
echo "  3. Download the RPMs listed above"
echo "  4. Place them in: $DEPS_DIR"
echo ""

# Check if files exist
RELEASE_RPM=$(ls "$DEPS_DIR"/oracle-instantclient-release-el8*.rpm 2>/dev/null | head -1)
BASIC_RPM=$(ls "$DEPS_DIR"/oracle-instantclient-basic*.rpm 2>/dev/null | head -1)

if [ -n "$RELEASE_RPM" ] && [ -n "$BASIC_RPM" ]; then
    echo "✓ Found Oracle RPMs:"
    echo "  Release: $(basename "$RELEASE_RPM")"
    echo "  Basic: $(basename "$BASIC_RPM")"
    echo ""
    echo "Verifying RPMs..."
    
    # Verify they are valid RPM files
    if file "$RELEASE_RPM" | grep -q "RPM"; then
        echo "  ✓ Release RPM is valid"
    else
        echo "  ✗ Release RPM appears to be invalid"
    fi
    
    if file "$BASIC_RPM" | grep -q "RPM"; then
        echo "  ✓ Basic RPM is valid"
    else
        echo "  ✗ Basic RPM appears to be invalid"
    fi
    
    echo ""
    echo "Oracle RPMs are ready for offline build!"
else
    echo "⚠ Missing Oracle RPMs:"
    [ -z "$RELEASE_RPM" ] && echo "  ✗ oracle-instantclient-release-el8*.rpm not found"
    [ -z "$BASIC_RPM" ] && echo "  ✗ oracle-instantclient-basic*.rpm not found"
    echo ""
    echo "Please download the missing RPMs and place them in: $DEPS_DIR"
fi

echo ""
echo "Alternative: Direct download links (requires Oracle account login):"
echo "  Release RPM:"
echo "    https://yum.oracle.com/repo/OracleLinux/OL8/oracle/instantclient/x86_64/getPackage/oracle-instantclient-release-el8-1.0-1.x86_64.rpm"
echo ""
echo "  Basic RPM:"
echo "    Check Oracle Instant Client downloads page for latest version"
echo "    https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html"
