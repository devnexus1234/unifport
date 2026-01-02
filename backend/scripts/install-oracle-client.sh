#!/usr/bin/env bash
# Script to install Oracle Instant Client on Ubuntu/Debian
# This is needed for local development without Docker

set -e

echo "=========================================="
echo "Oracle Instant Client Installation"
echo "=========================================="
echo ""

# Check if running on Ubuntu/Debian
if [ ! -f /etc/debian_version ]; then
    echo "Error: This script is for Ubuntu/Debian only"
    echo "For other systems, see: https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html"
    exit 1
fi

# Install required packages
echo "Installing required system packages..."
# Fix GPG key issues if any (common in WSL/older Ubuntu)
if ! sudo apt-get update 2>&1 | grep -q "NO_PUBKEY"; then
    echo "Package lists updated successfully"
else
    echo "Fixing GPG key issues..."
    MISSING_KEY=$(sudo apt-get update 2>&1 | grep -oP "NO_PUBKEY \K[0-9A-F]+" | head -1)
    if [ -n "$MISSING_KEY" ]; then
        echo "Adding missing GPG key: $MISSING_KEY"
        sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys "$MISSING_KEY" 2>/dev/null || \
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys "$MISSING_KEY" 2>/dev/null || true
    fi
    sudo apt-get update --allow-releaseinfo-change || sudo apt-get update
fi
sudo apt-get install -y libaio1 wget unzip

# Create directory for Oracle Instant Client
INSTANT_CLIENT_DIR="/opt/oracle/instantclient_21_1"
sudo mkdir -p /opt/oracle
cd /opt/oracle

echo ""
echo "Downloading Oracle Instant Client..."
echo ""

# Oracle Instant Client download URL (version 21.1.0.0.0)
# Note: Oracle requires accepting license agreement
DOWNLOAD_URL="https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.x64-21.1.0.0.0.zip"
EXPECTED_ZIP="/tmp/instantclient-basic-linux.x64-21.1.0.0.0.zip"
ZIP_FILE=""

# First, try to find existing zip file with flexible naming
echo "Looking for existing Oracle Instant Client zip file..."
# Search in common locations with flexible naming patterns (case-insensitive)
for search_dir in /tmp ~/Downloads "$(pwd)"; do
    if [ -d "$search_dir" ]; then
        ZIP_FILE=$(find "$search_dir" -maxdepth 1 -type f -iname "*instantclient*.zip" 2>/dev/null | head -1)
        if [ -n "$ZIP_FILE" ] && [ -f "$ZIP_FILE" ]; then
            break
        fi
    fi
done

if [ -n "$ZIP_FILE" ] && [ -f "$ZIP_FILE" ]; then
    echo "✓ Found existing zip file: $ZIP_FILE"
    echo "Using existing file (delete it if you want to re-download)"
else
    ZIP_FILE="$EXPECTED_ZIP"
    
    if [ -z "$ZIP_FILE" ]; then
        echo "Downloading Oracle Instant Client from Oracle website..."
        echo "Note: This requires accepting Oracle's license agreement"
        echo ""
        
        # Try to download with wget (accepting license)
        # Oracle requires a cookie/header to accept license, but we can try direct download
        echo "Attempting automatic download..."
        if wget --progress=bar:force --no-check-certificate \
            --header="Cookie: oraclelicense=accept-securebackup-cookie" \
            -O "$ZIP_FILE" "$DOWNLOAD_URL" 2>&1 | grep -q "200 OK\|saved"; then
            echo "✓ Download completed successfully"
        else
            # Try alternative method - direct download link
            echo "Trying alternative download method..."
            if curl -L -o "$ZIP_FILE" \
                -H "Cookie: oraclelicense=accept-securebackup-cookie" \
                "$DOWNLOAD_URL" 2>/dev/null && [ -f "$ZIP_FILE" ] && [ -s "$ZIP_FILE" ]; then
                echo "✓ Download completed successfully"
            else
                # Manual download required
                echo ""
                echo "⚠ Automatic download failed (Oracle may require manual acceptance of license)"
                echo ""
                echo "Please download manually:"
                echo "  1. Visit: https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html"
                echo "  2. Accept the license agreement"
                echo "  3. Download: instantclient-basic-linux.x64-21.1.0.0.0.zip"
                echo "  4. Place it in /tmp/ or ~/Downloads/"
                echo ""
                echo "Or try downloading with this command (after accepting license on website):"
                echo "  wget --header=\"Cookie: oraclelicense=accept-securebackup-cookie\" \\"
                echo "    -O $ZIP_FILE $DOWNLOAD_URL"
                echo ""
                read -p "Press Enter when you have downloaded the zip file to /tmp/, or Ctrl+C to cancel..."
                
                # Check again after manual download (with flexible naming)
                if [ ! -f "$ZIP_FILE" ] || [ ! -s "$ZIP_FILE" ]; then
                    ZIP_FILE=$(find /tmp ~/Downloads "$(pwd)" -maxdepth 1 \( -name "instantclient-basic-linux*.zip" -o -name "instantclient-basic-linuxx64.zip" \) 2>/dev/null | head -1)
                    if [ -z "$ZIP_FILE" ] || [ ! -f "$ZIP_FILE" ]; then
                        echo "Error: Oracle Instant Client zip file not found"
                        echo "Please download and place it in /tmp/ or ~/Downloads/"
                        echo "Accepted filenames: instantclient-basic-linux*.zip or instantclient-basic-linuxx64.zip"
                        exit 1
                    fi
                fi
            fi
        fi
    else
        echo "Found existing zip file: $ZIP_FILE"
    fi
fi

# Verify the zip file is valid
if [ ! -f "$ZIP_FILE" ] || [ ! -s "$ZIP_FILE" ]; then
    echo "Error: Invalid or missing zip file: $ZIP_FILE"
    exit 1
fi

echo "Using zip file: $ZIP_FILE"
echo "Extracting..."

# Extract
sudo unzip -q "$ZIP_FILE" -d /opt/oracle/

# Find the extracted directory
INSTANT_CLIENT_DIR=$(find /opt/oracle -maxdepth 1 -type d -name "instantclient_*" | head -1)

if [ -z "$INSTANT_CLIENT_DIR" ]; then
    echo "Error: Could not find extracted instantclient directory"
    exit 1
fi

echo "Found Oracle Instant Client at: $INSTANT_CLIENT_DIR"

# Set up library path
echo "Setting up library path..."
echo "$INSTANT_CLIENT_DIR" | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf > /dev/null
sudo ldconfig

# Set environment variables (add to ~/.bashrc)
echo ""
echo "Adding environment variables to ~/.bashrc..."
if ! grep -q "ORACLE_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Oracle Instant Client
export ORACLE_HOME=$INSTANT_CLIENT_DIR
export LD_LIBRARY_PATH=\$ORACLE_HOME:\$LD_LIBRARY_PATH
export PATH=\$ORACLE_HOME:\$PATH
EOF
    echo "✓ Added to ~/.bashrc"
else
    echo "✓ Already in ~/.bashrc"
fi

# Source it for current session
export ORACLE_HOME=$INSTANT_CLIENT_DIR
export LD_LIBRARY_PATH=$INSTANT_CLIENT_DIR:$LD_LIBRARY_PATH
export PATH=$INSTANT_CLIENT_DIR:$PATH

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Oracle Instant Client installed at: $INSTANT_CLIENT_DIR"
echo ""
echo "Environment variables added to ~/.bashrc"
echo "To use in current session, run:"
echo "  source ~/.bashrc"
echo ""
echo "Or in a new terminal, the variables will be loaded automatically"
echo ""
echo "Test installation:"
echo "  python -c 'import cx_Oracle; print(\"OK\")'"
