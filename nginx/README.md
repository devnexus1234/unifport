# Nginx Configuration for Unified Portal

This directory contains nginx configuration files with security features and SSL support for the Unified Portal application.

## Features

- **SSL/TLS Support**: Self-signed certificates for local development, ready for production certificates
- **Security Headers**: HSTS, X-Frame-Options, CSP, and more
- **Rate Limiting**: Protection against abuse on API and auth endpoints
- **Gzip Compression**: Optimized content delivery
- **Reverse Proxy**: Proxies requests to FastAPI backend and Angular frontend
- **HTTP to HTTPS Redirect**: Automatic redirect for secure connections

## Configuration Files

- `nginx.conf`: Main nginx configuration
- `conf.d/unified-portal.conf`: Production configuration (serves built frontend)
- `conf.d/unified-portal-dev.conf`: Development configuration (proxies to dev servers)
- `generate-ssl.sh`: Script to generate self-signed SSL certificates

## Quick Start

### Generate SSL Certificates

```bash
make nginx-generate-ssl
```

This creates self-signed certificates in `nginx/ssl/` for local development.

### Run Nginx for Local Development

```bash
# Make sure backend (port 8000) and frontend (port 4200) are running first
make nginx-dev
```

This will:
- Generate SSL certificates if they don't exist
- Start nginx container proxying to local services
- Access via: https://localhost:443

### Run Full Stack with Nginx

```bash
make dev-with-nginx
```

This starts Oracle DB, backend, frontend, and nginx together.

## Makefile Commands

```bash
make nginx-generate-ssl  # Generate SSL certificates
make nginx-start         # Start nginx (production mode)
make nginx-dev           # Start nginx (development mode)
make nginx-stop          # Stop nginx
make nginx-restart       # Restart nginx
make nginx-reload        # Reload configuration
make nginx-logs          # View nginx logs
make nginx-test          # Test nginx configuration
make nginx-remove        # Remove nginx container
```

## Security Features

### SSL/TLS
- TLS 1.2 and 1.3 only
- Strong cipher suites
- OCSP stapling support
- HSTS headers

### Security Headers
- `Strict-Transport-Security`: Forces HTTPS
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: XSS protection
- `Content-Security-Policy`: Restricts resource loading
- `Referrer-Policy`: Controls referrer information
- `Permissions-Policy`: Restricts browser features

### Rate Limiting
- API endpoints: 10 requests/second with burst of 20
- Auth endpoints: 5 requests/second with burst of 10

## Production Deployment

For production:

1. Replace self-signed certificates with real SSL certificates:
   ```bash
   # Place your certificates in nginx/ssl/
   cp your-cert.crt nginx/ssl/localhost.crt
   cp your-key.key nginx/ssl/localhost.key
   ```

2. Update `conf.d/unified-portal.conf` with your domain:
   ```nginx
   server_name your-domain.com;
   ```

3. Build frontend for production:
   ```bash
   cd frontend && npm run build --configuration=production
   ```

4. Start nginx:
   ```bash
   make nginx-start
   ```

## Development vs Production

- **Development** (`unified-portal-dev.conf`): Proxies to `localhost:8000` (backend) and `localhost:4200` (frontend dev server)
- **Production** (`unified-portal.conf`): Serves static files from `/usr/share/nginx/html` and proxies API to backend container

## Troubleshooting

### Certificate Warnings
Self-signed certificates will show browser warnings. This is expected for local development. Click "Advanced" and proceed.

### Port Conflicts
If ports 80 or 443 are already in use:
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Or modify ports in Makefile variables
```

### Test Configuration
```bash
make nginx-test
```

### View Logs
```bash
make nginx-logs
# Or
docker logs unified-portal-nginx
```

## Network Architecture

```
Internet
   ↓
Nginx (Port 443/80)
   ├─→ /api/* → Backend (Port 8000)
   └─→ /* → Frontend (Port 4200 or static files)
```
