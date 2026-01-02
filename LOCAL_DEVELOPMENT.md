# Local Development Guide (Without Docker)

This guide explains how to run the backend and frontend locally without Docker, while still using Docker for the Oracle database.

## Quick Start

### Step 1: Setup Database (One-time setup)

```bash
# This will:
#   - Start Oracle XE Docker container (if not running)
#   - Create/verify database users (umduser and umd schema)
#   - Run database migrations to create all tables
#   - Initialize database with default categories
#   - Create test user (username: testuser)
make setup-local-db ENV=development
```

**Note**: Run this command again whenever:
- Database schema changes (new migrations)
- You want to reset the database
- You're setting up on a new machine

### Step 2: Start Development Servers

**Option A: Run Both Together**

```bash
# Run both backend and frontend in parallel
make dev-local ENV=development
```

**Option B: Run Separately (Recommended for Development)**

Terminal 1 - Backend:
```bash
make dev-local-backend ENV=development
```

Terminal 2 - Frontend:
```bash
make dev-local-frontend
```

## What's Running Where

| Component | Location | Port |
|-----------|----------|------|
| Oracle Database | Docker Container | 1521 |
| Backend API | Local (Native) | 8000 |
| Frontend | Local (Native) | 4200 |

## Access Points

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:1521/XEPDB1

## Prerequisites

Before running local development, ensure you have:

1. **Python Virtual Environment**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Node.js Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Oracle Instant Client** (if not using Docker for database):
   - Not required if using `make setup-local-db` (uses Docker for Oracle)
   - Required if connecting to a local Oracle installation

4. **Docker** (for Oracle database only):
   - Must be installed and running
   - Used only for the Oracle XE container

## Available Commands

### Database Setup
```bash
make setup-local-db      # Setup database (Oracle + migrations + init)
make oracle-start        # Start Oracle container only
make oracle-stop         # Stop Oracle container
make migrate            # Run migrations (if Oracle Instant Client installed)
```

### Development Servers
```bash
make dev-local          # Run both BE+FE locally
make dev-local-backend  # Run backend only
make dev-local-frontend # Run frontend only
```

### Utilities
```bash
make stop              # Stop all local servers
make stop-backend      # Stop backend only
make stop-frontend     # Stop frontend only
make status            # Check what's running
```

## Benefits of Local Development

1. **Faster Iteration**: No Docker rebuild needed for code changes
2. **Better Debugging**: Direct access to logs and debuggers
3. **Native Performance**: No container overhead
4. **Hot Reload**: Both backend and frontend support hot reload
5. **IDE Integration**: Better integration with your IDE/debugger

## Troubleshooting

### Database Connection Issues

**Error**: `Oracle container is not running`

**Solution**:
```bash
make setup-local-db
```

### Port Already in Use

**Error**: `Port 8000 or 4200 already in use`

**Solution**:
```bash
make stop              # Stop all servers
# Or individually:
make stop-backend      # Stop backend
make stop-frontend     # Stop frontend
```

### Virtual Environment Not Found

**Error**: `venv/bin/activate: No such file or directory`

**Solution**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Dependencies Missing

**Error**: `npm: command not found` or module errors

**Solution**:
```bash
cd frontend
npm install
```

### Database Connection Issues

**Error**: `ORA-12505: Cannot connect to database. SID XEPDB1 is not registered`

**Solution**: The connection string format has been updated to use service name. Ensure your `.env.dev` file uses:
```env
DATABASE_URL=oracle+cx_oracle://umduser:umd123@localhost:1521/?service_name=XEPDB1
```

**Error**: `ORA-01017: invalid username/password; logon denied`

**Solution**: Users must be created before migrations. The `setup-local-db` command handles this automatically:
```bash
# This creates users if they don't exist
make setup-local-db ENV=development
```

### Database Migrations Failed

**Error**: Migration errors

**Solution**:
```bash
# Re-run database setup (this will create users and run migrations)
make setup-local-db ENV=development
```

## Workflow Example

```bash
# Day 1: Initial Setup
make setup              # Install all dependencies
make setup-local-db     # Setup database

# Daily Development
# Terminal 1
make dev-local-backend

# Terminal 2  
make dev-local-frontend

# When schema changes
make setup-local-db     # Re-run migrations

# End of day
make stop               # Stop all servers
```

## Comparison: Local vs Docker Development

| Feature | Local Development | Docker Development |
|---------|------------------|-------------------|
| Setup Speed | Fast (no image build) | Slower (image build) |
| Code Changes | Instant (hot reload) | Instant (volume mount) |
| Debugging | Native debugger | Container debugger |
| Performance | Native speed | Container overhead |
| Database | Docker container | Docker container |
| Isolation | Less isolated | Fully isolated |
| Use Case | Daily development | CI/CD, production-like |

## Next Steps

- See [README.md](README.md) for full documentation
- See [SETUP.md](SETUP.md) for detailed setup instructions
- See [CONFIG.md](CONFIG.md) for configuration options
