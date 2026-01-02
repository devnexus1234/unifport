# Offline Dependencies

This folder contains all external dependencies needed for offline Docker builds.

## Structure

```
deps/
├── oracle-rpms/          # Oracle Instant Client RPMs for RHEL/Oracle Linux
├── debian-packages/       # Debian packages for python:3.11-slim base image
└── python-wheels/         # Python wheel files (optional, if not using Nexus)
```

## Downloading Dependencies

Run the `download-deps.sh` script from a machine with internet access:

```bash
cd backend
./scripts/download-deps.sh
```

This will download:
- Oracle Instant Client RPMs (oracle-instantclient-release-el8, oracle-instantclient-basic)
- Debian packages (gcc, g++, libldap2-dev, libsasl2-dev, libaio-dev, libaio1)
- Python wheels (if not using Nexus repository)

## For RHEL Server Deployment

1. Copy the entire `deps/` folder to your RHEL server
2. Ensure Python packages are available in your internal Nexus repository
3. Build the Docker image using the offline Dockerfile:

```bash
docker build -f Dockerfile.offline -t unified-portal-backend .
```

## Notes

- Python dependencies should be configured to use your internal Nexus repository
- The Dockerfile.offline uses local files instead of downloading from the internet
- All system packages are installed from local .deb or .rpm files
