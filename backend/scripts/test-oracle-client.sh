#!/bin/bash
# Test script to verify Oracle client and libaio are working
set -e

echo "Testing Oracle client setup..."
echo ""

# Check if we're in a container
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container"
else
    echo "Running on host - will test in container"
    docker-compose run --rm --no-deps backend /app/scripts/test-oracle-client.sh
    exit $?
fi

echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo ""

# Check if libaio is accessible
echo "Checking for libaio..."
if ldconfig -p | grep -q libaio; then
    echo "✓ libaio found in ldconfig cache"
    ldconfig -p | grep libaio
else
    echo "⚠ libaio not in ldconfig cache, checking direct paths..."
fi

# Try to find libaio.so.1
if [ -f /lib/x86_64-linux-gnu/libaio.so.1 ] || [ -f /usr/lib/x86_64-linux-gnu/libaio.so.1 ]; then
    echo "✓ libaio.so.1 found in standard library paths"
    ls -lh /lib/x86_64-linux-gnu/libaio.so* 2>/dev/null || ls -lh /usr/lib/x86_64-linux-gnu/libaio.so* 2>/dev/null
else
    echo "✗ libaio.so.1 NOT found!"
    find /usr /lib -name "libaio.so*" 2>/dev/null | head -5
fi

echo ""
echo "Checking Oracle Instant Client..."
ORACLE_DIR=$(ls -d /usr/lib/oracle/*/client64 2>/dev/null | head -1)
if [ -n "$ORACLE_DIR" ]; then
    echo "✓ Oracle Instant Client found at: $ORACLE_DIR"
    if [ -f "$ORACLE_DIR/lib/libclntsh.so"* ]; then
        echo "✓ Oracle client library found"
        ls -lh "$ORACLE_DIR/lib/libclntsh.so"* | head -1
    else
        echo "✗ Oracle client library NOT found!"
    fi
else
    echo "✗ Oracle Instant Client NOT found!"
fi

echo ""
echo "Testing Python cx_Oracle import..."
if python -c "import cx_Oracle; print('✓ cx_Oracle imported successfully')" 2>&1; then
    echo "✓ Oracle client is working!"
    exit 0
else
    echo "✗ Failed to import cx_Oracle"
    python -c "import cx_Oracle" 2>&1 || true
    exit 1
fi
