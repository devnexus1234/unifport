# Offline Docker Build Setup Guide

This guide explains how to set up the backend Docker image for offline builds on an RHEL server without internet access.

## Prerequisites

1. A machine with internet access to download dependencies
2. Access to Oracle Instant Client downloads (requires Oracle account)
3. Internal Nexus repository configured for Python packages
4. Docker installed on the RHEL server

## Step 1: Download Dependencies (On Internet-Connected Machine)

### 1.1 Download Oracle Instant Client RPMs

Oracle Instant Client requires manual download from Oracle website:

1. Visit: https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html
2. Accept the license agreement
3. Download the following RPMs:
   - `oracle-instantclient-release-el8-1.0-1.x86_64.rpm`
   - `oracle-instantclient-basic-21.*.x86_64.rpm` (or latest version)

4. Place them in `backend/deps/oracle-rpms/`:
   ```bash
   mkdir -p backend/deps/oracle-rpms
   # Copy downloaded RPMs to this directory
   ```

### 1.2 Download Debian Packages

On a Debian/Ubuntu machine with internet access:

```bash
cd backend
./scripts/download-debian-packages.sh
```

This will download all required Debian packages to `deps/debian-packages/`.

Required packages:
- gcc
- g++
- libldap2-dev
- libsasl2-dev
- libaio-dev
- libaio1

### 1.3 (Optional) Download Python Wheels

If you're not using Nexus for Python packages:

```bash
cd backend
pip download -r requirements.txt -d deps/python-wheels
```

**Note:** If using Nexus repository, skip this step as packages will be installed from Nexus during build.

## Step 2: Configure Nexus for Python Packages

### 2.1 Create pip.conf

Create `backend/pip.conf` with your Nexus repository URL:

```ini
[global]
index-url = http://your-nexus-server:8081/repository/pypi-group/simple
trusted-host = your-nexus-server
```

Or use the example file:
```bash
cp backend/pip.conf.example backend/pip.conf
# Edit pip.conf with your Nexus URL
```

### 2.2 Alternative: Use Environment Variable

Set `PIP_INDEX_URL` during Docker build:
```bash
docker build --build-arg PIP_INDEX_URL=http://your-nexus:8081/repository/pypi-group/simple \
  -f Dockerfile.offline -t unified-portal-backend .
```

## Step 3: Transfer to RHEL Server

Copy the entire project to your RHEL server:

```bash
# On internet-connected machine
tar -czf unified-portal-offline.tar.gz \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='node_modules' \
  unified-portal/

# Transfer to RHEL server (using scp, USB, etc.)
scp unified-portal-offline.tar.gz user@rhel-server:/tmp/

# On RHEL server
cd /tmp
tar -xzf unified-portal-offline.tar.gz
cd unified-portal
```

## Step 4: Build Docker Image on RHEL Server

### 4.1 Verify Dependencies

Check that all dependencies are present:

```bash
cd backend

# Check Oracle RPMs
ls -lh deps/oracle-rpms/*.rpm

# Check Debian packages
ls -lh deps/debian-packages/*.deb

# Check pip.conf (if using local config)
cat pip.conf
```

### 4.2 Build with Nexus Repository

If using Nexus for Python packages:

```bash
# Option 1: Using pip.conf file
docker build -f Dockerfile.offline -t unified-portal-backend .

# Option 2: Using build argument
docker build \
  --build-arg PIP_INDEX_URL=http://your-nexus:8081/repository/pypi-group/simple \
  -f Dockerfile.offline \
  -t unified-portal-backend .
```

### 4.3 Build with Local Python Wheels

If using local Python wheels instead of Nexus:

1. Uncomment the wheel installation lines in `Dockerfile.offline`
2. Comment out the Nexus pip install lines
3. Build:

```bash
docker build -f Dockerfile.offline -t unified-portal-backend .
```

## Step 5: Verify Build

Test the built image:

```bash
# Check image was created
docker images | grep unified-portal-backend

# Test Oracle client
docker run --rm unified-portal-backend python -c "import cx_Oracle; print('Oracle client OK')"

# Test application
docker run --rm -p 8000:8000 unified-portal-backend
```

## Troubleshooting

### Issue: Oracle RPMs not found

**Error:** `Error: Oracle Instant Client not found`

**Solution:** 
- Verify RPMs are in `deps/oracle-rpms/`
- Check RPM file names match the pattern in Dockerfile
- Ensure RPMs are for the correct architecture (x86_64)

### Issue: Debian packages installation fails

**Error:** `dpkg: error processing package`

**Solution:**
- Ensure all dependency packages are downloaded
- Check package architecture matches (amd64)
- Try installing dependencies manually: `dpkg -i *.deb` then `apt-get install -f`

### Issue: Python packages not found

**Error:** `Could not find a version that satisfies the requirement`

**Solution:**
- Verify Nexus repository URL is correct
- Check Nexus repository has the required packages
- Test Nexus access: `pip install --index-url <nexus-url> <package>`
- If using local wheels, ensure all wheels are in `deps/python-wheels/`

### Issue: libaio.so.1 not found

**Error:** `libaio.so.1: cannot open shared object file`

**Solution:**
- Verify `libaio1` and `libaio-dev` packages are downloaded
- Check entrypoint.sh includes standard library paths
- Rebuild image after ensuring packages are present

## File Structure

After setup, your `backend/` directory should have:

```
backend/
├── deps/
│   ├── oracle-rpms/
│   │   ├── oracle-instantclient-release-el8-*.rpm
│   │   └── oracle-instantclient-basic-*.rpm
│   ├── debian-packages/
│   │   ├── gcc_*.deb
│   │   ├── g++_*.deb
│   │   ├── libldap2-dev_*.deb
│   │   ├── libsasl2-dev_*.deb
│   │   ├── libaio-dev_*.deb
│   │   └── libaio1_*.deb
│   └── python-wheels/  (optional)
│       └── *.whl files
├── Dockerfile.offline
├── pip.conf (or pip.conf.example)
└── ...
```

## Additional Notes

- The offline Dockerfile (`Dockerfile.offline`) is identical to `Dockerfile` except it uses local dependencies
- All internet downloads are replaced with local file copies
- Python packages are installed from Nexus repository (configured via pip.conf or environment variable)
- System packages are installed from local .deb files
- Oracle Instant Client is installed from local .rpm files

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify- **Python Dependencies**: `requirements.txt` (includes `oracledb`, `FastAPI`, `SQLAlchemy`, etc.) Check Docker build logs for specific error messages
4. Ensure Nexus repository is accessible and contains required packages
