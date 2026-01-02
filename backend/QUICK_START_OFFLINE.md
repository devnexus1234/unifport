# Quick Start: Offline Docker Build

## On Internet-Connected Machine

1. **Download Oracle RPMs:**
   ```bash
   cd backend
   ./scripts/download-oracle-rpms.sh
   # Follow instructions to manually download from Oracle website
   # Place RPMs in deps/oracle-rpms/
   ```

2. **Download Debian Packages:**
   ```bash
   ./scripts/download-debian-packages.sh
   ```

3. **Configure Nexus (if using):**
   ```bash
   cp pip.conf.example pip.conf
   # Edit pip.conf with your Nexus URL
   ```

4. **Transfer to RHEL Server:**
   ```bash
   tar -czf ../unified-portal-offline.tar.gz --exclude='.git' --exclude='venv' --exclude='node_modules' .
   # Transfer to RHEL server
   ```

## On RHEL Server (Offline)

1. **Extract and verify:**
   ```bash
   tar -xzf unified-portal-offline.tar.gz
   cd unified-portal/backend
   ls deps/oracle-rpms/*.rpm
   ls deps/debian-packages/*.deb
   ```

2. **Build Docker image:**
   ```bash
   # With Nexus (recommended)
   docker build \
     --build-arg PIP_INDEX_URL=http://your-nexus:8081/repository/pypi-group/simple \
     --build-arg PIP_TRUSTED_HOST=your-nexus \
     -f Dockerfile.offline \
     -t unified-portal-backend .
   
   # Or with pip.conf file
   docker build -f Dockerfile.offline -t unified-portal-backend .
   ```

3. **Verify:**
   ```bash
   docker run --rm unified-portal-backend python -c "import oracledb; print('OK')"
   # Python 3.11+ (Clean environment with `oracledb` installed)
   ```

## File Checklist

Before building, ensure you have:

- [ ] `deps/oracle-rpms/oracle-instantclient-release-el8-*.rpm`
- [ ] `deps/oracle-rpms/oracle-instantclient-basic-*.rpm`
- [ ] `deps/debian-packages/*.deb` (multiple files)
- [ ] `pip.conf` (if using Nexus, otherwise Python wheels in `deps/python-wheels/`)

## Troubleshooting

- **Missing RPMs:** Run `./scripts/download-oracle-rpms.sh` for instructions
- **Missing .deb files:** Run `./scripts/download-debian-packages.sh` on Debian/Ubuntu machine
- **Python packages not found:** Check Nexus URL or provide wheels in `deps/python-wheels/`

For detailed instructions, see `OFFLINE_SETUP.md`.
