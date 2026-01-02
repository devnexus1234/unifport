# Detailed Setup Guide

## 🚀 Quick Start (Using Makefile)

The fastest way to get started:

```bash
# 1. Complete setup
make setup

# 2. Edit backend/.env with your configuration
# (Database, LDAP, etc.)

# 3. Initialize database
make init-db

# 4. Start development servers
make dev
```

That's it! The application will be available at:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 Manual Setup

### 1. Backend Setup

**Important**: Before installing Python dependencies, install system-level dependencies:

```bash
# Install OpenLDAP development libraries (required for python-ldap)
sudo apt-get update
sudo apt-get install -y libldap2-dev libsasl2-dev build-essential python3-dev
```

Then proceed with Python setup:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Initialize database
alembic upgrade head
python scripts/init_db.py

# Run server
python run.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Database Setup

#### Oracle Database Configuration

**Option 1: Using Docker (Recommended)**
- No Oracle Instant Client needed - Oracle runs in a container
- Use `make oracle-start` to start the Oracle XE container

**Option 2: Using Local Oracle Database**

1. **Install Oracle Instant Client:**
   - Download from [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - **Linux**: Extract and set `LD_LIBRARY_PATH`
     ```bash
     export LD_LIBRARY_PATH=/path/to/instantclient_21_1:$LD_LIBRARY_PATH
     ```
   - **Windows**: Add Oracle Instant Client directory to `PATH`
   - **macOS**: Install via Homebrew or download from Oracle

2. **Create Database User:**
   ```sql
   CREATE USER portal_user IDENTIFIED BY portal_pass;
   GRANT CONNECT, RESOURCE TO portal_user;
   GRANT CREATE TABLE TO portal_user;
   ```

3. **Update .env:**
   ```env
   ORACLE_USER=portal_user
   ORACLE_PASSWORD=portal_pass
   ORACLE_HOST=localhost
   ORACLE_PORT=1521
   ORACLE_SERVICE=XE
   ```

4. **Run Migrations:**
   ```bash
   cd backend
   source venv/bin/activate
   alembic upgrade head
   ```

5. **Initialize Default Data:**
   ```bash
   python scripts/init_db.py
   ```

### 4. LDAP Configuration (Optional for Debug Mode)

If not using debug mode, configure LDAP:

```env
LDAP_SERVER=ldap://ldap.example.com:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=cn=users,dc=example,dc=com
LDAP_GROUP_DN=cn=groups,dc=example,dc=com
```

**For Development (Debug Mode):**
```env
DEBUG_MODE=true
```
This bypasses LDAP authentication - any username/password will work.

### 5. Create Initial Admin User

In debug mode, any user can login. To create an admin user:

**Option 1: Via Database**
```sql
-- After first login, update user
UPDATE users SET is_admin = 1 WHERE username = 'your_username';
```

**Option 2: Via API**
```bash
# Login first to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "any"}'

# Use token to update user (requires admin endpoint or direct DB access)
```

**Option 3: Programmatically**
Create a script to set admin flag during initialization.

## 📁 Default Categories

The system automatically creates these default categories:
- **Storage** - Storage automation catalogues
- **Firewall** - Firewall automation catalogues
- **Backup** - Backup automation catalogues
- **Network** - Network automation catalogues
- **Security** - Security automation catalogues
- **Monitoring** - Monitoring automation catalogues
- **Other** - Other automation catalogues

You can add more categories via the Admin panel after logging in.

## 🔐 First Login

In debug mode (`DEBUG_MODE=true`):
- ✅ Any username/password combination will work
- ✅ All users get default `admin` and `users` groups
- ✅ First login automatically creates the user in the database
- ✅ User is created with `is_active=True` but `is_admin=False`

**To make a user admin:**
```sql
UPDATE users SET is_admin = 1 WHERE username = 'your_username';
```

## 🚀 Production Deployment Checklist

Before deploying to production:

### Security
- [ ] Set `DEBUG_MODE=false` in `.env`
- [ ] Change `SECRET_KEY` to a secure random string (use `openssl rand -hex 32`)
- [ ] Configure proper LDAP settings
- [ ] Update CORS origins to production domains only
- [ ] Enable HTTPS/TLS
- [ ] Review and restrict API endpoints if needed

### Database
- [ ] Set up proper Oracle database credentials
- [ ] Configure database connection pooling
- [ ] Set up database backups
- [ ] Test database failover scenarios
- [ ] Review database indexes for performance

### Application
- [ ] Configure proper logging (file-based or centralized)
- [ ] Set up log rotation
- [ ] Configure production WSGI server (Gunicorn + Uvicorn)
- [ ] Set up process manager (systemd, supervisor, etc.)
- [ ] Configure reverse proxy (nginx, Apache)
- [ ] Set up monitoring and alerting

### Frontend
- [ ] Build production bundle: `make build-frontend`
- [ ] Configure production API URL
- [ ] Set up CDN for static assets
- [ ] Enable production optimizations
- [ ] Test all routes and features

### RBAC & Permissions
- [ ] Review and test RBAC permissions
- [ ] Set up proper user roles
- [ ] Configure Distribution Lists (DLs)
- [ ] Test catalogue access controls
- [ ] Document permission structure

### Testing
- [ ] Run full test suite: `make test`
- [ ] Perform security audit
- [ ] Load testing
- [ ] End-to-end testing
- [ ] User acceptance testing

## 🔧 Development Tips

### Using Makefile

```bash
# Check what commands are available
make help

# Quick status check
make status

# Clean everything and start fresh
make clean-all
make setup
```

### Database Migrations

```bash
# Create a new migration
make migrate-create MESSAGE="Add new field"

# Apply migrations
make migrate

# Reset database (careful!)
make db-reset
```

### Debugging

1. **Backend Issues:**
   - Check logs in terminal
   - Verify `.env` configuration
   - Test database connection
   - Check API docs at `/docs`

2. **Frontend Issues:**
   - Check browser console
   - Verify API URL in services
   - Check Network tab for API calls
   - Verify CORS settings

3. **Database Issues:**
   - Test connection: `sqlplus user/pass@host:port/service`
   - Check migrations: `alembic current`
   - View migration history: `alembic history`

## 📞 Need Help?

- Check the main [README.md](../README.md) for troubleshooting
- Review API documentation at http://localhost:8000/docs
- Check service status: `make status`
- Verify environment: `make check-env`

