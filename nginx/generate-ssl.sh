#!/bin/bash
# Generate self-signed SSL certificate for local development

set -e

SSL_DIR="nginx/ssl"
CERT_FILE="$SSL_DIR/localhost.crt"
KEY_FILE="$SSL_DIR/localhost.key"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Check if certificates already exist
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificates already exist at $SSL_DIR"
    echo "To regenerate, delete the existing certificates first:"
    echo "  rm $CERT_FILE $KEY_FILE"
    exit 0
fi

echo "Generating self-signed SSL certificate for localhost..."

# Generate private key
openssl genrsa -out "$KEY_FILE" 2048

# Generate certificate signing request
openssl req -new -key "$KEY_FILE" -out "$SSL_DIR/localhost.csr" \
    -subj "/C=US/ST=State/L=City/O=Unified Portal/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:::1"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in "$SSL_DIR/localhost.csr" \
    -signkey "$KEY_FILE" -out "$CERT_FILE" \
    -extensions v3_req \
    -extfile <(echo "[v3_req]"; echo "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:::1")

# Remove CSR file
rm "$SSL_DIR/localhost.csr"

# Set proper permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo "✓ SSL certificate generated successfully!"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"
echo ""
echo "Note: This is a self-signed certificate for local development only."
echo "Your browser will show a security warning - this is expected."
