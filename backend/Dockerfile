# Backend Dockerfile
# Multi-stage build to get Oracle Instant Client
FROM oraclelinux:8 AS oracle-client
RUN dnf install -y oracle-instantclient-release-el8 && \
    dnf install -y oracle-instantclient-basic && \
    dnf clean all

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libldap2-dev \
    libsasl2-dev \
    libaio-dev \
    libaio1 \
    && rm -rf /var/lib/apt/lists/* && \
    ldconfig && \
    # Verify libaio is installed and find its location
    find /usr -name "libaio.so*" 2>/dev/null | head -5 && \
    ldconfig -p | grep libaio || true

# Copy Oracle Instant Client from oracle-client stage
# Copy the entire oracle directory (handles any version: 21, 23, etc.)
COPY --from=oracle-client /usr/lib/oracle /usr/lib/oracle
# Detect installed version and set up library paths
RUN ORACLE_DIR=$(ls -d /usr/lib/oracle/*/client64 2>/dev/null | head -1) && \
    if [ -z "$$ORACLE_DIR" ]; then \
        echo "Error: Oracle Instant Client not found" && exit 1; \
    fi && \
    echo "$$ORACLE_DIR/lib" > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    # Also add standard library paths to ld.so.conf for system libraries
    echo "/lib/x86_64-linux-gnu" >> /etc/ld.so.conf.d/oracle-instantclient.conf && \
    echo "/usr/lib/x86_64-linux-gnu" >> /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig && \
    echo "Detected Oracle Instant Client at: $$ORACLE_DIR" && \
    ls -la "$$ORACLE_DIR/lib/libclntsh.so"* 2>/dev/null | head -1 && \
    # Verify libaio can be found
    ldconfig -p | grep libaio || echo "Warning: libaio not found in ldconfig cache"
# Copy entrypoint script that sets ORACLE_HOME dynamically at runtime
# Copy it early so it's available before other COPY operations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    test -f /entrypoint.sh && \
    head -1 /entrypoint.sh | grep -q '#!/bin/sh' && \
    echo "Entrypoint script created successfully"
# Set default ENV (will be overridden by entrypoint script at runtime)
# Include standard library paths for system libraries like libaio
# These paths are where Debian/Ubuntu store system libraries
ENV ORACLE_HOME=/usr/lib/oracle/21/client64
ENV LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib:/usr/lib/oracle/23/client64/lib:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu
ENV PATH=/usr/lib/oracle/21/client64/bin:/usr/lib/oracle/23/client64/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure entrypoint script is at root level (COPY . . might have copied it to /app)
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh && \
    chmod 755 /entrypoint.sh && \
    ls -la /entrypoint.sh && \
    head -1 /entrypoint.sh

# Run tests and validate coverage (fails build if coverage < 70% or services < 95%)
RUN python scripts/validate_coverage.py || { \
    echo ""; \
    echo "========================================"; \
    echo "❌ BUILD FAILED: Coverage requirements not met"; \
    echo "Required: Overall >= 70%, Services >= 95%"; \
    echo "========================================"; \
    exit 1; \
}

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown appuser:appuser /entrypoint.sh && \
    chmod 755 /entrypoint.sh

# Use entrypoint to set Oracle environment before running commands
ENTRYPOINT ["/entrypoint.sh"]

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
