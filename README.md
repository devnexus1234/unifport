# Unified Portal

[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![Frontend](https://img.shields.io/badge/Frontend-Angular-dd0031.svg?style=flat-square&logo=angular&logoColor=white)](https://angular.io) [![Database](https://img.shields.io/badge/Database-Oracle-F80000?style=flat-square&logo=oracle&logoColor=white)](https://www.oracle.com/database)

A comprehensive unified portal application for managing multiple automation-related catalogues. Built with **FastAPI** backend and **Angular** frontend.

---

## Table of Contents

- [Features](#-features)
- [Quick Start](#️-quick-start)
  - [Prerequisites](#prerequisites)
  - [Option 1: Using Makefile](#option-1-using-makefile-recommended)
  - [Option 2: Manual Setup](#option-2-manual-setup)
- [Initial Setup Guide](#-initial-setup-guide)
  - [Step 1: Start Oracle Database](#step-1-start-oracle-database)
  - [Step 2: Create Database User and Schema](#step-2-create-database-user-and-schema)
  - [Step 3: Update Backend Configuration](#step-3-update-backend-configuration)
  - [Step 4: Run Database Migrations](#step-4-run-database-migrations)
  - [Step 5: Creating and Updating Migrations](#step-5-creating-and-updating-migrations)
- [Configuration](#️-configuration)
  - [Multi-Environment Configuration](#multi-environment-configuration)
  - [Environment Variables](#environment-variables)
  - [App-Level Configuration](#app-level-configuration)
- [Dark Theme](#-dark-theme)
- [Authentication & User Management](#-authentication--user-management)
  - [Debug Mode](#debug-mode-development)
  - [Creating Users](#creating-users)
  - [JWT Authentication](#jwt-authentication)
- [RBAC (Role-Based Access Control)](#-rbac-role-based-access-control)
  - [Overview](#overview)
  - [Seeding Menus and Roles](#seeding-menus-and-roles)
  - [Admin Panel](#admin-panel)
  - [Assigning Roles to Users](#assigning-roles-to-users)
  - [Documentation](#documentation)
- [Environments & Modes](#-environments--modes)
  - [Debug Mode (Development)](#debug-mode-development)
  - [Production Mode](#production-mode)
  - [Configuration Mapping](#configuration-mapping)

## Environments & Modes

### Debug Mode (Development)
Debug mode is designed for rapid local development. It intentionally bypasses complex authentication requirements.

**How to Run:**
```bash
make dev ENV=development
```
**Key Characteristics:**
*   **Authentication**: **Bypassed**. You can login with any username/password (if user exists in DB). `DEBUG_MODE=True` in config.
*   **Security**: CSRF and strict CORS checks are relaxed.
*   **Configuration**: Loads `backend/.env.dev`.
*   **Frontend**: Runs via `ng serve` (JIT compilation, hot-reload).
*   **Backend**: Runs via `uvicorn` with hot-reload enabled.

### Production Mode
Production mode is for deployment. It enforces strict security, requires real authentication (LDAP/JWT), and uses optimized builds.

**How to Run:**
1.  **Build Frontend**:
    ```bash
    make build
    ```
2.  **Run Backend**:
    ```bash
    make run-backend ENV=production
    ```
3.  **Serve Frontend**:
    Serve the artifacts from `frontend/dist/` using Nginx or Apache. See the [Production Deployment](#-production-deployment) section.

**Key Characteristics:**
*   **Authentication**: **Enforced**. Users must authenticate via LDAP. `DEBUG_MODE=False`.
*   **Configuration**: Loads `backend/.env.prod`.
*   **Performance**: Frontend AOT compilation, tree-shaking, and minimized assets. Backend reload disabled.

### Configuration Mapping
The application automatically loads the correct configuration file based on the `ENV` variable passed to `make` or the `ENVIRONMENT` environment variable.

1.  **Initialize Files**:
    ```bash
    make init-env
    ```
    This creates the base templates:
    *   `backend/.env.dev`
    *   `backend/.env.staging`
    *   `backend/.env.prod`

2.  **Customize Per Environment**:
    *   **Development (`.env.dev`)**:
        ```dotenv
        DEBUG=True
        DEBUG_MODE=True

# Bypasses LDAP
        ```
    *   **Production (`.env.prod`)**:
        ```dotenv
        DEBUG=False
        DEBUG_MODE=False

# Enforces LDAP
        LDAP_SERVER=ldap://your-server
        SECRET_KEY=...

# Use a strong, unique key
        ```

3.  **Switching Environments**:
    You don't need to rename files. Just pass the env flag:
    ```bash

# Runs with .env.staging settings
    make run-backend ENV=staging
    ```

## Additional Resources
  - [API Documentation](#api-documentation)
  - [Project Structure](#project-structure)
  - [Morning Checklist Module](backend/app/modules/linux/morning_checklist/README.md)
  - [IPAM Module](frontend/src/app/modules/network/ipam/README.md)
- [Production Deployment](#-production-deployment)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Nginx Setup](#nginx-setup)
- [Background Jobs and Workers](#-background-jobs-and-workers)
  - [Overview](#overview)
  - [Available Workers](#available-workers)
  - [Creating a New Worker](#creating-a-new-worker)
  - [Trigger Types](#trigger-types)
  - [Managing Jobs](#managing-jobs)
  - [Job Schedules from Environment Variables](#job-schedules-from-environment-variables)
- [Testing Background Workers](#-testing-background-workers)
  - [Overview](#overview-1)
  - [Running Tests](#running-tests)
  - [Writing Tests for Workers](#writing-tests-for-workers)
- [Email Service](#-email-service)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Environment-Specific Configuration](#environment-specific-configuration)
  - [SMTP Providers](#smtp-providers)
  - [Email Service Methods](#email-service-methods)
- [Docker Deployment](#-docker-deployment)
  - [Prerequisites](#prerequisites-1)
  - [Quick Start](#quick-start)
  - [Docker Services](#docker-services)
  - [Docker Commands](#docker-commands)
  - [Environment Configuration](#environment-configuration)
  - [Development Mode](#development-mode)
  - [Production Deployment](#production-deployment-1)
  - [Docker Images](#docker-images)
  - [Networking](#networking)
  - [Volumes](#volumes)
  - [Health Checks](#health-checks)
  - [Troubleshooting](#troubleshooting)
- [Error Handling & Logging](#-error-handling--logging)
  - [HTTP Status Codes](#http-status-codes)
  - [Error Response Format](#error-response-format)
  - [Logging & Tracing](#logging--tracing)
- [License](#-license)
- [Contributing](#-contributing)
- [Support](#-support)

## Documentation

### Backend Documentation
- **[Backend README](./backend/README.md)** - Complete backend setup and development guide
- **[Testing Guide](./backend/TESTING_GUIDE.md)** - Comprehensive guide to writing tests and achieving 75%+ coverage
- **[Testing Quick Reference](./backend/README_TESTING.md)** - Quick commands and patterns for testing
- **[Coverage Validation](./backend/docs/COVERAGE_VALIDATION.md)** - Coverage requirements and validation
- **[RBAC System](./backend/docs/RBAC_SYSTEM.md)** - Role-Based Access Control documentation

### Setup & Deployment
- **[Quick Start (Offline)](./backend/QUICK_START_OFFLINE.md)** - Complete offline setup guide
- **[Offline Setup](./backend/OFFLINE_SETUP.md)** - Detailed offline installation instructions
- **[Dependencies](./backend/deps/README.md)** - Offline dependencies and package management

### Module Documentation
- **[Morning Checklist Module](./backend/app/modules/linux/morning_checklist/README.md)** - Morning checklist feature documentation
- **[IPAM Module](./frontend/src/app/modules/network/ipam/README.md)** - IP Address Management module

### Testing & Quality Assurance
**Current Coverage**: 84.62% overall, 11/11 business logic files â‰¥75% âœ…

See [Testing Guide](./backend/TESTING_GUIDE.md) for:
- Writing integration and unit tests
- Achieving 75%+ coverage
- Common testing patterns
- Troubleshooting guide
- Validation commands

---

## Features

- **Multi-Catalogue Management**: Organize catalogues under categories (Storage, Firewall, Backup, etc.)
- **API-Powered**: All catalogues and menu items are dynamically loaded from the API
- **Admin Interface**: Full admin panel to add, edit, enable/disable catalogues
- **RBAC (Role-Based Access Control)**: Control access to catalogues and menu items at user or Distribution List (DL) level
- **LDAP Authentication**: Enterprise-grade authentication with LDAP integration
- **JWT Authentication**: Secure JWT-based authentication with refresh tokens
- **Multi-Environment Support**: Separate configurations for dev, staging, and production
- **Dark Theme**: Full dark theme support with automatic system preference detection
- **Debug Mode**: Bypass LDAP and password checks for development
- **Oracle Database**: Enterprise database support
- **Professional UI**: Modern, responsive Angular Material design
- **Makefile Support**: Easy commands for setup, development, and deployment
- **Background Jobs**: Scheduled workers for daily tasks, token cleanup, status checks, and more

## Quick Start

### Prerequisites

- **Python 3.9+** (with pip)
  - **Note**: Python 3.13 requires SQLAlchemy 2.0.31+ (automatically installed)
- **Node.js 18+** (with npm)
- **Docker** (for Oracle XE container and Nginx - recommended)
- **OpenSSL** (for generating SSL certificates)
- **Oracle Database 12c+** (or compatible, if not using Docker)
- **LDAP Server** (optional for debug mode)
- **Make** (for using Makefile commands)

### External System Dependencies

Before installing Python packages, you need to install the following system-level dependencies:

#### For Linux (Ubuntu/Debian)

```bash

# Install OpenLDAP development libraries (required for python-ldap)
sudo apt-get update
sudo apt-get install -y libldap2-dev libsasl2-dev

# Install build tools (if not already installed)
sudo apt-get install -y build-essential gcc python3-dev
```

#### For Oracle Database Connectivity

**Option 1: Using Docker (Recommended)**
- No additional setup needed - Oracle runs in a container
- Uses `gvenzl/oracle-xe:latest` image (community-maintained, no authentication required)
- The `make oracle-start` command handles everything automatically:
  - Pulls the Oracle XE image from Docker Hub
  - Creates and starts the container
  - Creates database users and schemas
  - Runs migrations to create all tables
  - Initializes database with default data
- **Backend Docker Image**: Uses multi-stage build with Oracle Linux to install Oracle Instant Client
  - The Dockerfile automatically installs Oracle Instant Client from Oracle's official repository
  - No manual download or installation required
  - Works reliably without authentication issues

**Option 2: Using Local Oracle Database**
- **Oracle Instant Client** must be installed on your system
- Download from [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
- **Linux**: Extract and set `LD_LIBRARY_PATH`
  ```bash
  export LD_LIBRARY_PATH=/path/to/instantclient_21_1:$LD_LIBRARY_PATH
  ```
- **Windows**: Add Oracle Instant Client directory to `PATH`
- **macOS**: Install via Homebrew or download from Oracle

**Important Notes:**
- If you don't have Oracle Instant Client installed locally, use Docker-based commands:
  - `make init-db-docker` instead of `make init-db`
  - `make migrate-docker` instead of `make migrate`
- The backend Docker image uses a multi-stage build:
  - Stage 1: Oracle Linux 8 installs Oracle Instant Client via official package manager
  - Stage 2: Python image copies the libraries from stage 1
  - This approach is more reliable than direct downloads and avoids 404 errors

#### For macOS

```bash

# Install OpenLDAP development libraries
brew install openldap

# Install build tools
xcode-select --install
```

#### For Windows (WSL)

If using WSL (Windows Subsystem for Linux), follow the Linux instructions above.

#### Quick Installation Script

A helper script is available to install system dependencies:

```bash

# Run the installation script (Linux/Ubuntu)
cd backend
bash install_deps.sh
```

This script will:
1. Install `libldap2-dev` and `libsasl2-dev` (required for `python-ldap`)
2. Create virtual environment if it doesn't exist
3. Install all Python dependencies from `requirements.txt`
4. Verify installation

**Note**: The `python-ldap` package requires OpenLDAP development headers to compile. Without `libldap2-dev` and `libsasl2-dev`, pip installation will fail with errors like:
```
fatal error: lber.h: No such file or directory
```

#### Summary of External Dependencies

| Dependency | Purpose | Required For | Installation |
|

---

-

---

-

---

-|

---

-

---

--|

---

-

---

-

---

---|

---

-

---

-

---

--|
| `libldap2-dev` | OpenLDAP development headers | `python-ldap` package | `sudo apt-get install libldap2-dev` |
| `libsasl2-dev` | SASL development libraries | `python-ldap` package | `sudo apt-get install libsasl2-dev` |
| `build-essential` | GCC compiler and build tools | Compiling Python packages | `sudo apt-get install build-essential` |
| `python3-dev` | Python development headers | Compiling Python packages | `sudo apt-get install python3-dev` |
| Oracle Instant Client | Oracle database connectivity | `cx_Oracle` package (if not using Docker) | Download from Oracle website |
| Docker | Container runtime | Oracle XE container | `sudo apt-get install docker.io` |

**Important**: These system dependencies must be installed **before** running `pip install -r requirements.txt` or `make install-backend`.

### Option 1: Using Makefile (Recommended)

#### Initial Setup

```bash

# 1. Complete setup (installs dependencies, creates .env file)
make setup

# 2. Run the application with Oracle database (recommended)

# This will:

#   - Start Oracle XE Docker container

#   - Run database migrations

#   - Initialize database with default categories

#   - Create a test user (username: testuser)

#   - Start both backend and frontend servers
make dev-with-db ENV=development
```

The application will be available at:
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### Running with Nginx (Production-like Setup)

For a production-like setup with SSL and security features:

```bash

# 1. Generate SSL certificates (first time only)
make nginx-generate-ssl

# 2. Start backend and frontend in separate terminals, then:
make nginx-dev

# Or run everything together:
make dev-with-nginx
```

The application will be available at:
- **HTTPS**: https://localhost:443 (via nginx with SSL)
- **HTTP**: http://localhost:80 (redirects to HTTPS)
- **Direct Backend**: http://localhost:8000
- **Direct Frontend**: http://localhost:4200

**Note**: Browser will show a security warning for self-signed certificates. This is expected for local development.

#### Creating Your First User

After running `make dev-with-db`, a test user is automatically created. However, to create additional users or admin users:

```bash

# Create an admin user (replace 'admin' with your desired username)
make create-admin USERNAME=admin

# Or create a regular user
make create-admin USERNAME=myuser
```

**Note**: In debug mode (default for development), authentication is bypassed, but users must still exist in the database. Use `make create-admin` to create users before they can login.

#### Local Development Without Docker (Backend & Frontend)

For local development where you want to run backend and frontend natively (without Docker), but still use Docker for Oracle database:

**Step 1: Setup Database (One-time or when schema changes)**

```bash

# This will:

#   - Start Oracle XE Docker container (if not running)

#   - Run database migrations to create all tables

#   - Initialize database with default categories

#   - Create test user
make setup-local-db ENV=development
```

**Step 2: Start Backend Locally**

In one terminal:
```bash

# Run backend server locally (connects to Oracle in Docker)
make dev-local-backend ENV=development
```

**Step 3: Start Frontend Locally**

In another terminal:
```bash

# Run frontend development server locally
make dev-local-frontend
```

**Or run both together:**

```bash

# Run both backend and frontend locally (in parallel)
make dev-local ENV=development
```

**Note**: The database still runs in Docker, but backend and frontend run natively on your machine. This gives you:
- Faster development iteration (no Docker rebuild needed for code changes)
- Direct access to logs and debugging
- Native performance
- Hot reload for both backend and frontend

**Available Local Development Commands:**
```bash
make setup-local-db

# Setup database (Oracle in Docker + creates users + migrations + init)
make dev-local-backend

# Run backend locally (requires setup-local-db first)
make dev-local-frontend

# Run frontend locally
make dev-local

# Run both BE+FE locally (requires setup-local-db first)
```

**Note**: `make setup-local-db` automatically:
- Starts Oracle XE container (if not running)
- Creates/verifies database users (`umduser` and `umd` schema)
- Runs database migrations
- Initializes database with default data
- Creates test user

#### Alternative: Run Without Database Container

If you have an existing Oracle database (not in Docker):

```bash

# Initialize database with default categories
make init-db

# Run both backend and frontend in development mode
make dev ENV=development
```

**Note**: If you don't have Oracle Instant Client installed locally, use Docker-based commands:
```bash

# Use Docker-based initialization (no local Oracle Instant Client needed)
make init-db-docker

# Use Docker-based migrations
make migrate-docker
```

**Available Makefile Commands:**

```bash
make help

# Show all available commands
make setup

# Complete setup (backend + frontend + env)
make install-backend

# Install backend dependencies
make install-frontend

# Install frontend dependencies
make init-env

# Initialize .env file from .env.example
make init-db

# Initialize database with default categories
make migrate

# Run database migrations
make migrate-create

# Create new migration (MESSAGE="description")
make run-backend

# Run only backend server (ENV=development)
make run-frontend

# Run only frontend server
make dev

# Run both backend and frontend in parallel (ENV=development)
make dev-with-db

# Run with Oracle database container (recommended)
make setup-local-db

# Setup local database (Oracle in Docker + migrations + init)
make dev-local-backend

# Run backend locally without Docker (requires setup-local-db)
make dev-local-frontend

# Run frontend locally without Docker
make dev-local

# Run both BE+FE locally without Docker (requires setup-local-db)
make dev-with-nginx

# Run full stack with nginx (backend, frontend, nginx)
make create-admin

# Create admin/user (usage: make create-admin USERNAME=admin)
make create-test-user

# Create test user (username: testuser)
make oracle-start

# Start Oracle XE container
make oracle-stop

# Stop Oracle XE container
make oracle-remove

# Remove Oracle XE container
make nginx-generate-ssl

# Generate SSL certificates for local development
make nginx-start

# Start nginx container (production mode)
make nginx-dev

# Start nginx for local development
make nginx-stop

# Stop nginx container
make nginx-restart

# Restart nginx container
make nginx-reload

# Reload nginx configuration
make nginx-logs

# View nginx logs
make nginx-test

# Test nginx configuration
make nginx-remove

# Remove nginx container
make build

# Build both for production
make test

# Run all tests
make lint

# Lint all code
make clean

# Clean all artifacts
make status

# Check service status
make check-env

# Check environment setup
```

## Initial Setup Guide

This guide walks you through the complete initial setup process, from starting the database to running your first migration.

### Step 1: Start Oracle Database

The application uses Oracle XE database running in a Docker container.

#### Using Makefile (Recommended)

```bash

# Start Oracle XE container
make oracle-start
```

This command will:
- Create and start the Oracle XE Docker container
- Expose port 1521 for database connections
- Wait for Oracle to be ready (takes 1-2 minutes)
- Create the database user (`umduser`) and schema (`umd`) with password `umd123`
- Verify the connection
- **Automatically run database migrations** (if virtual environment not found, uses Docker)
- **Automatically initialize database** with default data (if virtual environment not found, uses Docker)

#### Manual Docker Command

```bash
docker run -d \
  --name unified-portal-oracle \
  -p 1521:1521 \
  -p 5500:5500 \
  -e ORACLE_PASSWORD=umd123 \
  gvenzl/oracle-xe:latest
```

**Note**: The `gvenzl/oracle-xe` image is a community-maintained Oracle XE image that doesn't require Oracle Container Registry authentication. It's easier to use and publicly available on Docker Hub.

#### Verify Database is Running

```bash

# Check container status
docker ps | grep unified-portal-oracle

# View database logs
make oracle-logs
```

### Step 2: Create Database User and Schema

If you started the database using `make oracle-start`, the user and schema are automatically created. However, if you need to create them manually or recreate them:

#### Using Makefile

```bash

# Create/update Oracle user (umduser) and schema (umd)
make oracle-create-user
```

This creates:
- **User**: `umduser` with password `umd123`
- **Schema**: `umd` with password `umd123`
- Both have CONNECT, RESOURCE, and DBA privileges
- Both have UNLIMITED TABLESPACE

#### Manual SQL Commands

If you prefer to create users manually, connect to the Oracle container:

```bash

# Connect to Oracle container
docker exec -it unified-portal-oracle sqlplus / as sysdba
```

Then run:

```sql
-- Switch to pluggable database
ALTER SESSION SET CONTAINER=XEPDB1;

-- Create user
CREATE USER umduser IDENTIFIED BY "umd123";
GRANT CONNECT, RESOURCE, DBA TO umduser;
GRANT UNLIMITED TABLESPACE TO umduser;
ALTER USER umduser DEFAULT TABLESPACE USERS;
ALTER USER umduser TEMPORARY TABLESPACE TEMP;

-- Create schema
CREATE USER umd IDENTIFIED BY "umd123";
GRANT CONNECT, RESOURCE, DBA TO umd;
GRANT UNLIMITED TABLESPACE TO umd;
ALTER USER umd DEFAULT TABLESPACE USERS;
ALTER USER umd TEMPORARY TABLESPACE TEMP;

EXIT;
```

#### Verify User Connection

Test the connection from your terminal:

```bash
docker exec -it unified-portal-oracle sqlplus umduser/umd123@XEPDB1
```

Or using DBeaver:
- **Database Type**: Oracle
- **Host**: `localhost`
- **Port**: `1521`
- **Service Name**: `XEPDB1` (or SID: `XE` for older clients)
- **Username**: `umduser` (or `umd` for schema)
- **Password**: `umd123`
- **Schema**: `umd` (optional, can be left empty or set to `umd`)
- **Connection Type**: Service Name (recommended) or SID

**DBeaver Connection Steps:**
1. Open DBeaver â†’ New Database Connection
2. Select **Oracle** from the database list
3. Fill in connection details:
   - **Host**: `localhost`
   - **Port**: `1521`
   - **Database/Schema**: `XEPDB1` (Service Name) or leave empty
   - **Username**: `umduser`
   - **Password**: `umd123`
4. Click **Test Connection** to verify
5. Click **Finish** to save and connect

**Note**: After running `make oracle-start`, all tables will be automatically created and ready to view in DBeaver.

**Viewing Tables in DBeaver:**
After connecting, expand the database tree:
- `unified-portal-oracle` â†’ `Schemas` â†’ `UMDUSER` â†’ `Tables`
- You should see all application tables (users, catalogues, categories, etc.)
- Right-click on any table â†’ **View Data** to see the contents

**Common Tables Created:**
- `users` - Application users
- `catalogue_categories` - Catalogue categories (Storage, Firewall, Backup, etc.)
- `catalogues` - Catalogue items
- `alembic_version` - Migration version tracking
- And other application-specific tables

### Step 3: Update Backend Configuration

Update the backend configuration files with the database credentials.

#### Update `backend/app/core/config.py`

The default configuration is already set, but verify these values:

```python

# Database Configuration
ORACLE_USER: str = "umduser"
ORACLE_PASSWORD: str = "umd123"
ORACLE_HOST: str = "localhost"
ORACLE_PORT: int = 1521
ORACLE_SERVICE: str = "XEPDB1"
```

#### Update Environment Files

Create or update environment-specific files:

**`backend/.env.dev`** (Development):
```env
ENVIRONMENT=development
DEBUG=True

# Database Configuration

# Note: Use ?service_name=XEPDB1 (not /XEPDB1) for pluggable databases
DATABASE_URL=oracle+cx_oracle://umduser:umd123@localhost:1521/?service_name=XEPDB1
ORACLE_USER=umduser
ORACLE_PASSWORD=umd123
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1

# JWT Security
SECRET_KEY=dev-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug Mode (bypasses LDAP)
DEBUG_MODE=True

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
```

**`backend/.env.staging`** and **`backend/.env.prod`**:
- Use the same structure but with production credentials
- Set `DEBUG=False` and `DEBUG_MODE=False`
- Use a strong `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- Configure proper LDAP settings

#### Initialize Environment Files

```bash

# Create environment files if they don't exist
make init-env
```

### Step 4: Run Database Migrations

Migrations create and update database tables based on your SQLAlchemy models.

#### Using Makefile (Recommended)

```bash

# Run all pending migrations
make migrate
```

This command:
- Activates the virtual environment
- Runs `alembic upgrade head`
- Applies all pending migrations to create/update tables

#### Using Docker (If backend container is running)

```bash

# Run migrations in backend container
docker-compose exec backend alembic upgrade head
```

#### Using Docker Compose (One-off container) - Recommended when Oracle Instant Client not installed

If you don't have Oracle Instant Client installed locally, use the Docker-based approach:

**Using Makefile (Easiest):**
```bash

# Run migrations in Docker container
make migrate-docker

# Initialize database in Docker container
make init-db-docker
```

**Manual Docker Compose:**
```bash

# Build backend image first (if not already built)

# The Dockerfile uses multi-stage build to install Oracle Instant Client
docker-compose build backend

# Run migrations in a temporary container
docker-compose run --rm --no-deps \
  -e DATABASE_URL="oracle+cx_oracle://umduser:umd123@oracle:1521/?service_name=XEPDB1" \
  -e ORACLE_HOST=oracle \
  -e ORACLE_USER=umduser \
  -e ORACLE_PASSWORD=umd123 \
  -e ORACLE_PORT=1521 \
  -e ORACLE_SERVICE=XEPDB1 \
  -e ENVIRONMENT=development \
  backend bash -c "cd /app && alembic upgrade head"
```

**About the Oracle Database Image:**
- Uses `gvenzl/oracle-xe:latest` - a community-maintained Oracle XE image
- No Oracle Container Registry authentication required
- Publicly available on Docker Hub (no login needed)
- Automatically creates pluggable database `XEPDB1` on first start
- Default admin users: `SYS` and `SYSTEM` (password set via `ORACLE_PASSWORD` environment variable)
- **Connection String**: `oracle+cx_oracle://umduser:umd123@localhost:1521/?service_name=XEPDB1`
  
  **Important**: Use `/?service_name=XEPDB1` (not `/XEPDB1`) when connecting to Oracle XE pluggable databases. This ensures Oracle interprets it as a service name rather than a SID.

**About the Backend Docker Image:**
- Uses multi-stage build with Oracle Linux 8 to install Oracle Instant Client
- Installs `oracle-instantclient-basic` from Oracle's official repository (automatically detects version: 21, 23, etc.)
- Copies libraries to Python 3.11-slim base image
- Includes entrypoint script (`entrypoint.sh`) that dynamically sets `ORACLE_HOME` at runtime
- More reliable than direct downloads (avoids 404 errors and authentication issues)
- Entrypoint script automatically detects installed Oracle Instant Client version and configures environment variables

#### Manual Migration Command

If you have Oracle Instant Client installed:

```bash
cd backend
source venv/bin/activate

# or: . venv/bin/activate
export DATABASE_URL="oracle+cx_oracle://umduser:umd123@localhost:1521/?service_name=XEPDB1"
alembic upgrade head
```

#### Verify Migrations

After running migrations, verify tables were created:

```bash

# Connect to database
docker exec -it unified-portal-oracle sqlplus umduser/umd123@XEPDB1
```

```sql
-- List all tables
SELECT table_name FROM user_tables;

-- Check migration version
SELECT * FROM alembic_version;
```

### Step 5: Creating and Updating Migrations

When you modify database models (add/remove tables, columns, indexes, etc.), you need to create and apply migrations.

#### Creating a New Migration

**Using Makefile:**

```bash

# Create a new migration with description
make migrate-create MESSAGE="Add user email field"
```

**Manual Command:**

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Add user email field"
```

This will:
- Analyze your SQLAlchemy models
- Compare with current database schema
- Generate a migration file in `backend/alembic/versions/`
- Include SQL statements to apply the changes

#### Review Generated Migration

**Important**: Always review the generated migration file before applying it!

```bash

# View the latest migration file
ls -lt backend/alembic/versions/ | head -2
cat backend/alembic/versions/<latest_migration_file>.py
```

Check for:
- Correct table/column names
- Appropriate data types
- Foreign key constraints
- Indexes
- Any manual adjustments needed

#### Common Migration Scenarios

**1. Adding a New Table:**

```python

# In your model file (e.g., backend/app/models/example.py)
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
```

Then create migration:
```bash
make migrate-create MESSAGE="Add examples table"
```

**2. Adding a Column to Existing Table:**

```python

# Modify existing model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))

# New column
```

Then create migration:
```bash
make migrate-create MESSAGE="Add email column to users table"
```

**3. Modifying Column Type:**

```python

# Change column type
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)

# Changed from String(50)
```

**4. Adding Foreign Key:**

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

# New foreign key
    user = relationship("User", back_populates="posts")
```

**5. Adding Index:**

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), index=True)

# Add index
```

#### Applying Migrations

After creating and reviewing migrations:

```bash

# Apply all pending migrations
make migrate
```

Or manually:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

#### Rolling Back Migrations

If you need to rollback:

```bash
cd backend
source venv/bin/activate

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations (careful!)
alembic downgrade base
```

#### Migration Best Practices

1. **Always Review**: Check generated migrations before applying
2. **Test First**: Test migrations on development database
3. **Backup**: Backup production database before migrations
4. **One Change Per Migration**: Keep migrations focused and atomic
5. **Descriptive Messages**: Use clear migration messages
6. **Version Control**: Commit migration files to git
7. **Test Rollback**: Verify you can rollback if needed

#### Troubleshooting Migrations

**Issue: Migration conflicts**
```bash

# Check current migration version
alembic current

# View migration history
alembic history

# Resolve conflicts by editing migration files manually
```

**Issue: Migration fails**
```bash

# Check migration status
alembic current

# View detailed error in logs

# Fix the issue in the migration file

# Re-run migration
alembic upgrade head
```

**Issue: Models out of sync**
```bash

# Regenerate migration (be careful!)
alembic revision --autogenerate -m "Sync models"

# Review and apply
alembic upgrade head
```

### Complete Setup Checklist

- [ ] Oracle database container is running (`make oracle-start`)
- [ ] Database user and schema created (`make oracle-create-user`)
- [ ] Backend configuration updated (`backend/app/core/config.py` and `.env.dev`)
- [ ] Environment files initialized (`make init-env`)
- [ ] Database migrations applied (`make migrate`)
- [ ] Database initialized with default data (`make init-db`)
- [ ] Test user created (`make create-test-user` or `make create-admin USERNAME=admin`)

## Configuration

### Multi-Environment Configuration

The project supports multiple environments with separate configuration files:

#### Backend Environments

- **Development**: `backend/.env.dev`
- **Staging**: `backend/.env.staging`
- **Production**: `backend/.env.prod`

Set the environment using:
```bash
export ENVIRONMENT=development

# or staging, production
```

Or when running:
```bash
make run-backend ENV=development
make run-backend ENV=staging
make run-backend ENV=production
```

#### Frontend Environments

- **Development**: `frontend/src/environments/environment.ts`
- **Staging**: `frontend/src/environments/environment.staging.ts`
- **Production**: `frontend/src/environments/environment.prod.ts`

Build for different environments:
```bash

# Development (default)
npm start

# Staging
ng build --configuration=staging

# Production
ng build --configuration=production
```

### Environment Variables

The application supports multi-environment configuration. Environment-specific `.env` files are automatically loaded based on the `ENVIRONMENT` variable.

#### Environment Files

The backend uses the following environment files:
- **`.env.dev`** - Development environment (default, pre-configured with `umd` schema)
- **`.env.staging`** - Staging environment (contains placeholders)
- **`.env.prod`** - Production environment (contains placeholders)

#### Setting the Environment

Set the `ENVIRONMENT` variable to switch between environments:

```bash

# Development (default)
export ENVIRONMENT=development

# or
make run-backend ENV=development

# Staging
export ENVIRONMENT=staging

# or
make run-backend ENV=staging

# Production
export ENVIRONMENT=production

# or
make run-backend ENV=production
```

#### Initializing Environment Files

Run `make init-env` to check/create the environment files. Then update each file with your specific settings:

```bash
make init-env
```

#### Environment File Structure

Each environment file (`.env.dev`, `.env.staging`, `.env.prod`) contains:

```env

# Environment
ENVIRONMENT=development

# or staging/production
DEBUG=True

# False for staging/production

# Database Configuration (using umd schema)
DATABASE_URL=oracle+cx_oracle://umd:portal_pass@localhost:1521/?service_name=XEPDB1
ORACLE_USER=umd
ORACLE_PASSWORD=portal_pass
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1

# JWT Security
SECRET_KEY=your-secret-key

# Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LDAP Configuration
LDAP_ENABLED=False

# True for staging/production
LDAP_SERVER=ldap://ldap.example.com:389

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# Debug Mode
DEBUG_MODE=True

# False for staging/production

# Logging
LOG_LEVEL=DEBUG

# INFO for staging, WARNING for production
```

**Important Notes:**
- `.env.dev` is pre-configured for local development with the `umd` schema
- `.env.staging` and `.env.prod` contain placeholder values marked with `CHANGE_ME_*`
- **Never commit actual secrets to version control** - these files are in `.gitignore`
- Update database credentials, LDAP settings, and SECRET_KEY for each environment
- Generate strong SECRET_KEYs for staging/production using: `openssl rand -hex 32`

#### Frontend (environment.ts)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Unified Portal',
  theme: {
    defaultTheme: 'light',
    enableThemeToggle: true
  }
};
```

### App-Level Configuration

Application-level settings that are the same across environments but configurable:

**Backend** (`backend/app/core/app_config.py`):
- UI settings (title, description, version)
- Pagination defaults
- File upload limits
- Theme defaults
- Security policies
- Branding (colors, logos)

**Access via API**:
```bash
GET /api/v1/config/app

# Public app config
GET /api/v1/config/environment

# Environment config (requires auth)
```

## Dark Theme

The application includes full dark theme support:

- **Toggle Theme**: Click the theme icon in the toolbar
- **Auto Mode**: Automatically follows system preference
- **Persistent**: Theme preference is saved in localStorage
- **Smooth Transitions**: All theme changes are animated

### Theme Modes

- **Light**: Light color scheme
- **Dark**: Dark color scheme
- **Auto**: Follows system preference

### Customization

Theme colors can be customized via:
1. CSS variables in `frontend/src/styles.scss`
2. App config API (`/api/v1/config/app`)
3. Environment configuration

## Authentication & User Management

### Debug Mode (Development)

In debug mode (enabled by default in development), the application:
- **Bypasses LDAP authentication** - Any username/password combination will work for authentication
- **Requires users to exist** - Users must be created before they can login

**Login Credentials in Debug Mode:**
- **Username**: Any existing username in the database
- **Password**: Any password (authentication is bypassed)

### Creating Users

Users must be created before they can login. To create users:

```bash

# Create an admin user
make create-admin USERNAME=admin

# Create a regular user
make create-admin USERNAME=myuser
```

**Note**: The `create-admin` command creates users with admin privileges. Users must exist in the database before they can login, even in debug mode.

### JWT Authentication

The application uses JWT-based authentication with refresh tokens:

#### Features

## RBAC (Role-Based Access Control)

### Overview

The Unified Management Portal implements a comprehensive Role-Based Access Control (RBAC) system that controls access to menus and catalogues based on user roles. This system provides fine-grained access control across the application.

**Key Concepts:**
- **Menus**: Top-level navigation items (e.g., Storage, Backup, Firewall, Linux)
- **Catalogues**: Items under each menu (e.g., "Storage Configuration", "Backup Restore")
- **Roles**: Collections of permissions assigned to users
- **Menu Permissions**: Control access to entire menus and all their catalogues
- **Catalogue Permissions**: Refine access to specific catalogues within a menu

### Admin Role

The system includes a special **"Admin"** role that provides full access to all menus and catalogues. Users can have admin privileges in two ways:

1. **`is_admin` flag** (Legacy method): Boolean flag on the User model
2. **"Admin" role** (RBAC method): Role-based assignment via RBAC system

Both methods are supported and checked throughout the system. The `is_admin_user()` utility function checks both:
- If `user.is_admin == True`, OR
- If user has the "Admin" role assigned

**Benefits of Admin Role:**
- Can be assigned/removed via RBAC system (like other roles)
- Visible in role management interface
- Can be tracked and audited
- Consistent with RBAC model

### How RBAC Works

#### Permission Hierarchy

The RBAC system uses a two-level permission model:

1. **Menu-Level Permissions** (Default Access)
   - If a user has a menu-level role (e.g., "Storage Menu Admin"), they get access to **ALL catalogues** in that menu
   - Example: User with "Storage Menu Admin" role can access all Storage catalogues

2. **Catalogue-Level Permissions** (Refinement)
   - If a user has specific catalogue-level permissions, they get access to **only those specific catalogues**
   - Example: User with "Backup Configuration Access" role can only access the "Backup Configuration" catalogue
   - Catalogue-level permissions take precedence over menu-level permissions (more restrictive)

#### Access Control Logic

When checking if a user can access a catalogue:

1. **First**: Check if user has specific catalogue-level permission â†’ If yes, grant access (refinement)
2. **Second**: Check if user has menu-level permission â†’ If yes, grant access to all catalogues in menu (default)
3. **Admin users**: Always have full access to everything

#### Permission Types

Each permission can have one of three types:
- **`read`**: View-only access
- **`write`**: Can create and modify
- **`admin`**: Full administrative access (includes read and write)

### Seeding Menus and Roles

After initializing the database, seed the default menus, catalogues, and roles:

```bash

# Seed menus, catalogues, and roles (includes Admin role)
make seed-menus

# Seed test users with specific role configurations
make seed-test-users

# Test RBAC configuration
make test-rbac
```

**Note**: The `seed-menus` script automatically creates the "Admin" role with full permissions to all menus and catalogues. This role can be assigned to users via the User-Role Management interface (debug mode) or via API/database.

**Default Roles Created:**
- **Admin Role**: "Admin"
  - System-wide administrator role with full access to all menus and catalogues
  - Can be assigned to users via RBAC system
  - Alternative to `is_admin` flag for role-based admin access
  
- **Menu-Level Roles**: `{Menu Name} Menu Admin` and `{Menu Name} Menu User`
  - Example: "Storage Menu Admin", "Storage Menu User"
  - These roles grant access to ALL catalogues in the menu
  
- **Catalogue-Level Roles**: `{Catalogue Name} Access`
  - Example: "Backup Configuration Access"
  - These roles grant access to only that specific catalogue

**Test Users Created:**
- `user1`: Admin user with all access (has "Admin" role)
- `user2`: Storage-only access (has "Storage Menu Admin" role)
- `user3`: Storage and Firewall access (has both "Storage Menu Admin" and "Firewall Menu Admin" roles)
- `user4`: Backup Configuration only (has "Backup Configuration Access" role)

**Admin Role:**
- The system includes a special "Admin" role that provides full access to all menus and catalogues
- Users can have admin privileges via:
  1. `is_admin` flag on the User model (legacy method)
  2. "Admin" role assignment (RBAC method)
- Both methods are supported and checked throughout the system

### Admin Panel

Access the admin panel at `/admin` (requires admin privileges) to manage:

**âš ️ Debug Mode Features:**
Some features in the admin panel are only available when the application is running in debug mode (`enableDebug: true`). These features include:
- **User-Role Management**: Visual interface for assigning roles to users (only visible in debug mode)

In production, these features are hidden for security. Use API endpoints or direct database access instead.

#### 1. Role Management

**Create and Manage Roles:**
- Create new roles with custom names and descriptions
- Edit role details (name, description)
- Delete (deactivate) roles

**API Endpoints:**
- `GET /api/v1/admin/roles` - List all roles
- `GET /api/v1/admin/roles/{role_id}` - Get role with permissions
- `POST /api/v1/admin/roles` - Create new role
- `PUT /api/v1/admin/roles/{role_id}` - Update role
- `DELETE /api/v1/admin/roles/{role_id}` - Deactivate role

#### 2. Menu Permission Assignment

**Assign Menu Permissions to Roles:**
- Select which menus a role can access
- Set permission type (read/write/admin) for each menu
- Menu-level permissions grant access to ALL catalogues in that menu

**API Endpoints:**
- `POST /api/v1/admin/roles/{role_id}/menu-permissions` - Assign menu permission
- `DELETE /api/v1/admin/roles/{role_id}/menu-permissions/{menu_id}` - Remove menu permission

**Example:**
```bash

# Assign "read" permission on Storage menu to a role
curl -X POST http://localhost:8000/api/v1/admin/roles/1/menu-permissions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"menu_id": 1, "permission_type": "read"}'
```

#### 3. Catalogue Permission Assignment

**Assign Catalogue Permissions to Roles:**
- Select which catalogues a role can access
- Set permission type (read/write/admin) for each catalogue
- Catalogue-level permissions refine access to specific catalogues only

**API Endpoints:**
- `POST /api/v1/admin/roles/{role_id}/catalogue-permissions` - Assign catalogue permission
- `DELETE /api/v1/admin/roles/{role_id}/catalogue-permissions/{catalogue_id}` - Remove catalogue permission

**Example:**
```bash

# Assign "read" permission on a specific catalogue to a role
curl -X POST http://localhost:8000/api/v1/admin/roles/1/catalogue-permissions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"catalogue_id": 1, "permission_type": "read"}'
```

#### 4. User-Role Assignment (Debug Mode Only)

**âš ️ Important**: User-role assignment via the admin panel is only available when the application is running in **debug mode** (`enableDebug: true` in `environment.ts`). In production, user-role assignments should be managed via the API or database directly for security.

**Features:**
- View all users and their assigned roles
- Assign roles to users
- Remove roles from users
- Visual indication of admin users

**Access:**
- Navigate to Admin Panel â†’ "User-Role Management" tab
- This tab is only visible when `enableDebug: true` in the environment configuration

**API Endpoints:**
- `GET /api/v1/admin/users` - List all users with their roles
- `GET /api/v1/admin/users/{user_id}/roles` - Get user's roles
- `POST /api/v1/admin/users/{user_id}/roles` - Assign role to user
- `DELETE /api/v1/admin/users/{user_id}/roles/{role_id}` - Remove role from user

**Example API Usage:**
```bash

# Assign a role to a user
curl -X POST http://localhost:8000/api/v1/admin/users/1/roles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1, "is_dl": false, "dl_name": null}'

# Remove a role from a user
curl -X DELETE http://localhost:8000/api/v1/admin/users/1/roles/1 \
  -H "Authorization: Bearer <token>"
```

**Debug Mode Configuration:**
- **Development**: `frontend/src/environments/environment.ts` - `enableDebug: true` (default)
- **Production**: `frontend/src/environments/environment.prod.ts` - `enableDebug: false` (default)
- **Staging**: `frontend/src/environments/environment.staging.ts` - `enableDebug: true` (default)

**Security Note:**
In production environments, the User-Role Management tab is hidden. User-role assignments should be managed through:
1. Direct database access (for administrators)
2. API endpoints (with proper authentication and authorization)
3. Automated scripts or deployment processes

### Assigning Roles to Users

#### Method 1: Using Admin API (Recommended)

Use the admin API endpoints to assign roles:

```bash

# Get all users
curl http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer <token>"

# Assign role to user
curl -X POST http://localhost:8000/api/v1/admin/users/{user_id}/roles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"role_id": 1, "is_dl": false}'
```

#### Method 2: Direct Database Insert

```sql
-- Assign a role to a user
INSERT INTO user_role_mapping (user_id, role_id, is_dl, dl_name)
VALUES (
    (SELECT id FROM users WHERE username = 'john.doe'),
    (SELECT id FROM roles WHERE name = 'Storage Menu Admin'),
    false,
    NULL
);
```

#### Method 3: Using Python Script

```python
from app.core.database import SessionLocal
from app.models.user import User
from app.models.rbac import Role, UserRole

db = SessionLocal()

user = db.query(User).filter(User.username == 'john.doe').first()
role = db.query(Role).filter(Role.name == 'Storage Menu Admin').first()

if user and role:
    user_role = UserRole(user_id=user.id, role_id=role.id, is_dl=False)
    db.add(user_role)
    db.commit()
    print(f"Assigned role '{role.name}' to user '{user.username}'")

db.close()
```

### RBAC Examples

#### Example 1: Menu-Level Access

**Scenario**: User needs access to all Storage catalogues

**Solution**:
1. Create or use existing role: "Storage Menu Admin"
2. Assign menu permission: "Storage Menu Admin" â†’ "Storage" menu (admin permission)
3. Assign role to user: User â†’ "Storage Menu Admin"

**Result**: User can access ALL catalogues in the Storage menu

#### Example 2: Catalogue-Level Access (Refinement)

**Scenario**: User needs access to only "Backup Configuration" catalogue

**Solution**:
1. Create role: "Backup Configuration Access"
2. Assign menu permission: "Backup Configuration Access" â†’ "Backup" menu (read permission) - needed to show menu
3. Assign catalogue permission: "Backup Configuration Access" â†’ "Backup Configuration" catalogue (read permission)
4. Assign role to user: User â†’ "Backup Configuration Access"

**Result**: User can see Backup menu but only access "Backup Configuration" catalogue

#### Example 3: Multiple Roles

**Scenario**: User needs Storage and Firewall access

**Solution**:
1. Assign role: User â†’ "Storage Menu Admin"
2. Assign role: User â†’ "Firewall Menu Admin"

**Result**: User can access all Storage catalogues AND all Firewall catalogues

### Menu Visibility

Menus are shown in the sidebar if:
- User has menu-level permission (MenuPermission) for that menu
- Even if the menu has no accessible catalogues, it will still be shown

This allows menus to be visible when roles are assigned, even before catalogues are configured.

### Catalogue Visibility

Catalogues are shown within a menu if:
1. User has specific catalogue-level permission (CatalogueRolePermission) for that catalogue, OR
2. User has menu-level permission (MenuPermission) for the parent menu

**Priority**: Catalogue-level permissions are checked first (refinement), then menu-level permissions (default access).

### Testing RBAC

Use the test script to verify RBAC configuration:

```bash

# Run RBAC test script
make test-rbac
```

This script:
- Tests all test users (user1, user2, user3, user4)
- Verifies menu and catalogue access based on roles
- Prints detailed access summary for each user

### Troubleshooting

**Issue**: User can't see a menu they should have access to

**Solution**:
1. Check if user has menu-level permission: `SELECT * FROM menu_permissions WHERE role_id IN (SELECT role_id FROM user_role_mapping WHERE user_id = ?)`
2. Verify role is assigned: `SELECT * FROM user_role_mapping WHERE user_id = ?`
3. Check menu is active: `SELECT * FROM menus WHERE id = ? AND is_active = true`

**Issue**: User can't access a catalogue they should have access to

**Solution**:
1. Check catalogue-level permissions: `SELECT * FROM catalogue_role_permissions WHERE role_id IN (SELECT role_id FROM user_role_mapping WHERE user_id = ?) AND catalogue_id = ?`
2. Check menu-level permissions: `SELECT * FROM menu_permissions WHERE role_id IN (SELECT role_id FROM user_role_mapping WHERE user_id = ?) AND menu_id = (SELECT menu_id FROM catalogues WHERE id = ?)`
3. Verify catalogue is enabled: `SELECT * FROM catalogues WHERE id = ? AND is_enabled = true AND is_active = true`

### Documentation

For detailed RBAC documentation, see:
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Database Schema**: See `backend/app/models/rbac.py` for model definitions
- **Permission Logic**: See `backend/app/api/v1/menu.py` and `backend/app/api/v1/catalogues.py` for access control implementation

### JWT Authentication

The application uses JWT-based authentication with refresh tokens:

#### Features

- **Access Tokens**: Short-lived tokens (default: 30 minutes)
- **Refresh Tokens**: Long-lived tokens (default: 7 days)
- **Automatic Refresh**: Frontend automatically refreshes expired tokens
- **Secure Claims**: Includes issuer, audience, and token type
- **Token Validation**: Full JWT validation with signature verification

### Token Structure

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "is_admin": false
  }
}
```

### API Endpoints

- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Frontend Integration

The frontend automatically:
- Stores tokens in localStorage
- Adds tokens to API requests
- Refreshes expired tokens
- Redirects to login on auth failure

## Additional Resources

### API Documentation

Once the backend is running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Project Structure

```
unified-portal/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ api/v1/

# API endpoints
â”‚   â”‚   â”‚   â”œâ”€â”€ network/

# Network category (e.g., ipam.py)
â”‚   â”‚   â”‚   â””â”€â”€ ...
â”‚   â”‚   â”œâ”€â”€ modules/

# Complex modules (e.g., linux/morning_checklist)
â”‚   â”‚   â”œâ”€â”€ core/

# Core config (database, security, settings)
â”‚   â”‚   â”œâ”€â”€ models/

# SQLAlchemy database models
â”‚   â”‚   â””â”€â”€ schemas/

# Pydantic request/response schemas
â”‚   â”œâ”€â”€ .env.dev

# Development environment config
â”‚   â”œâ”€â”€ .env.staging

# Staging environment config
â”‚   â”œâ”€â”€ .env.prod

# Production environment config
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ environments/

# Environment configs
â”‚   â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”‚   â”œâ”€â”€ modules/

# Feature modules by Category/Catalogue
â”‚   â”‚   â”‚   â”‚   â”œâ”€â”€ network/

# e.g., ipam/
â”‚   â”‚   â”‚   â”‚   â””â”€â”€ linux/

# e.g., morning-checklist/
â”‚   â”‚   â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”‚   â””â”€â”€ guards/
â”‚   â”‚   â””â”€â”€ styles.scss

# Global styles with theme support
â”‚   â””â”€â”€ package.json
â””â”€â”€ Makefile
```

## Production Deployment

### Backend

1. Set environment:
```bash
export ENVIRONMENT=production
```

2. Configure `.env.prod` with production values

3. Build and run:
```bash
make build-backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

1. Build for production:
```bash
cd frontend
ng build --configuration=production
```

2. Serve with nginx (recommended)

### Nginx Setup

The project includes a production-ready nginx configuration with security features:

#### Features

- **SSL/TLS Support**: Ready for production certificates
- **Security Headers**: HSTS, CSP, X-Frame-Options, and more
- **Rate Limiting**: Protection against abuse
- **Gzip Compression**: Optimized content delivery
- **Reverse Proxy**: Proxies API requests to backend

#### Production Deployment with Nginx

1. **Generate or install SSL certificates**:
   ```bash

# For production, use real certificates from Let's Encrypt or your CA

# Place them in nginx/ssl/
   cp your-cert.crt nginx/ssl/localhost.crt
   cp your-key.key nginx/ssl/localhost.key
   ```

2. **Build frontend**:
   ```bash
   make build-frontend
   ```

3. **Update nginx configuration**:
   - Edit `nginx/conf.d/unified-portal.conf`
   - Update `server_name` with your domain
   - Adjust paths if needed

4. **Start nginx**:
   ```bash
   make nginx-start
   ```

5. **Test configuration**:
   ```bash
   make nginx-test
   ```

#### Local Development with Nginx

For local development with SSL:

```bash

# Generate self-signed certificates
make nginx-generate-ssl

# Start nginx (proxies to localhost:8000 and localhost:4200)
make nginx-dev

# Access via https://localhost:443
```

**Note**: Browser will show security warning for self-signed certificates. This is expected.

See `nginx/README.md` for detailed nginx documentation.

## Background Jobs and Workers

The application includes a background job scheduler service for running scheduled tasks like daily emails, token cleanup, status checks, etc.

### Overview

The background job service uses **APScheduler** (Advanced Python Scheduler) and is integrated with FastAPI. All jobs are automatically started when the FastAPI application starts.

### Available Workers

The following workers are configured by default:

1. **Token Cleaner** (`TokenCleanerWorker`)
   - **Schedule**: Daily at 2:00 AM
   - **Purpose**: Cleans up expired refresh tokens from the database
   - **Location**: `backend/app/services/workers/token_cleaner.py`

2. **Daily Checklist** (`DailyChecklistWorker`)
   - **Schedule**: Daily at 8:00 AM
   - **Purpose**: Sends daily checklist emails to active users
   - **Location**: `backend/app/services/workers/daily_checklist.py`

3. **Status Checker** (`StatusCheckerWorker`)
   - **Schedule**: Every 6 hours
   - **Purpose**: Performs system health checks (database, services, etc.)
   - **Location**: `backend/app/services/workers/status_checker.py`

### Creating a New Worker

To create a new background worker, follow these steps:

#### Step 1: Create Worker Class

Create a new file in `backend/app/services/workers/` (e.g., `my_worker.py`):

```python
from app.services.workers.base import BaseWorker
from app.models.user import User

# Import any models you need


class MyWorker(BaseWorker):
    """Description of what this worker does"""
    
    name = "my_worker"

# Unique identifier
    description = "Description of the worker"
    
    async def execute(self):
        """Implement your worker logic here"""
        db = self.get_db()
        
        try:

# Your worker logic
            self.logger.info("Worker started")

# Example: Query database
            users = db.query(User).filter(User.is_active == True).all()
            self.logger.info(f"Found {len(users)} active users")

# Do your work here

# ...
            
            self.logger.info("Worker completed successfully")
            
        except Exception as e:
            self.logger.error(f"Worker failed: {e}", exc_info=True)
            db.rollback()
            raise
```

**Important Notes:**
- Inherit from `BaseWorker`
- Set `name` and `description` class attributes
- Implement `async def execute(self)` method
- Use `self.get_db()` to get database session
- Use `self.logger` for logging
- The base class handles database cleanup automatically

#### Step 2: Register Worker in `__init__.py`

Add your worker to `backend/app/services/workers/__init__.py`:

```python
from app.services.workers.my_worker import MyWorker

__all__ = [

# ... existing workers
    "MyWorker",
]
```

#### Step 3: Register Job in Job Registry

Add your job to `backend/app/services/job_registry.py`:

```python
from app.services.workers.my_worker import MyWorker
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

def register_all_jobs():

# ... existing jobs

# Example 1: Run daily at 3:00 AM
    add_job(
        func=MyWorker().run,
        trigger=CronTrigger(hour=3, minute=0),
        id="my_worker_daily",
        name="My Daily Worker",
        replace_existing=True
    )

# Example 2: Run every 30 minutes
    add_job(
        func=MyWorker().run,
        trigger=IntervalTrigger(minutes=30),
        id="my_worker_interval",
        name="My Interval Worker",
        replace_existing=True
    )

# Example 3: Run on specific days (Monday-Friday at 9 AM)
    add_job(
        func=MyWorker().run,
        trigger=CronTrigger(day_of_week="mon-fri", hour=9, minute=0),
        id="my_worker_weekdays",
        name="My Weekday Worker",
        replace_existing=True
    )
```

### Trigger Types

You can use different trigger types for scheduling:

#### CronTrigger (Cron-style scheduling)

```python
from apscheduler.triggers.cron import CronTrigger

# Daily at 2:00 AM
CronTrigger(hour=2, minute=0)

# Every Monday at 9:00 AM
CronTrigger(day_of_week="mon", hour=9, minute=0)

# First day of month at midnight
CronTrigger(day=1, hour=0, minute=0)

# Every weekday at 8:30 AM
CronTrigger(day_of_week="mon-fri", hour=8, minute=30)
```

#### IntervalTrigger (Time intervals)

```python
from apscheduler.triggers.interval import IntervalTrigger

# Every 5 minutes
IntervalTrigger(minutes=5)

# Every 1 hour
IntervalTrigger(hours=1)

# Every 30 seconds
IntervalTrigger(seconds=30)

# Every 2 days
IntervalTrigger(days=2)
```

#### DateTrigger (One-time execution)

```python
from apscheduler.triggers.date import DateTrigger
from datetime import datetime

# Run at specific date/time
DateTrigger(run_date=datetime(2025, 12, 25, 10, 0, 0))
```

### Managing Jobs

You can manage jobs programmatically:

```python
from app.services.scheduler import (
    get_jobs,
    pause_job,
    resume_job,
    remove_job
)

# Get all jobs
jobs = get_jobs()
for job in jobs:
    print(f"{job.id}: {job.name} - Next run: {job.next_run_time}")

# Pause a job
pause_job("my_worker_daily")

# Resume a job
resume_job("my_worker_daily")

# Remove a job
remove_job("my_worker_daily")
```

### Best Practices

1. **Error Handling**: Always wrap your logic in try-except blocks
2. **Logging**: Use `self.logger` for all logging (automatically includes worker name)
3. **Database**: Use `self.get_db()` to get database session, it's automatically closed
4. **Idempotency**: Make workers idempotent (safe to run multiple times)
5. **Resource Cleanup**: The base class handles database cleanup, but clean up other resources
6. **Testing**: Test workers independently before adding to scheduler
7. **Monitoring**: Log important events for monitoring and debugging

### Example: Complete Worker Implementation

```python
from app.services.workers.base import BaseWorker
from app.models.user import User
from datetime import datetime, timedelta


class UserActivityReportWorker(BaseWorker):
    """Generates and sends weekly user activity reports"""
    
    name = "user_activity_report"
    description = "Weekly user activity report generator"
    
    async def execute(self):
        """Generate and send activity reports"""
        db = self.get_db()
        
        try:

# Get users active in the last week
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_users = db.query(User).filter(
                User.is_active == True,
                User.last_login >= week_ago
            ).all()
            
            self.logger.info(f"Generating reports for {len(active_users)} users")
            
            for user in active_users:
                try:

# Generate report data
                    report_data = {
                        "user": user.username,
                        "login_count": 0,

# Calculate from logs
                        "last_login": user.last_login,

# ... more data
                    }

# Send email (implement email sending)

# await send_email(user.email, "Activity Report", report_data)
                    
                    self.logger.info(f"Report sent to {user.email}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to send report to {user.email}: {e}")
                    continue
            
            self.logger.info("Activity report generation completed")
            
        except Exception as e:
            self.logger.error(f"Error in activity report worker: {e}", exc_info=True)
            db.rollback()
            raise
```

Then register it:

```python

# In job_registry.py
add_job(
    func=UserActivityReportWorker().run,
    trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),

# Every Monday at 9 AM
    id="user_activity_report_weekly",
    name="Weekly User Activity Report",
    replace_existing=True
)
```

### Worker Lifecycle

1. **Initialization**: Worker instance is created
2. **Execution**: `execute()` method is called
3. **Database**: Session is automatically created and closed
4. **Error Handling**: Exceptions are caught and logged
5. **Cleanup**: Resources are cleaned up automatically

### Monitoring and Debugging

- All worker executions are logged with the worker name
- Check application logs for worker execution status
- Use `get_jobs()` to see all scheduled jobs and their next run times
- Workers run in the same process as the FastAPI application

### Job Schedules from Environment Variables

Job schedules are configured per environment using environment variables:

**Environment Variables:**
- `JOB_TOKEN_CLEANER_SCHEDULE` - Schedule for token cleanup (default: `"0 2 * * *"` - daily at 2 AM)
- `JOB_DAILY_CHECKLIST_SCHEDULE` - Schedule for daily checklist emails (default: `"0 8 * * *"` - daily at 8 AM)
- `JOB_STATUS_CHECKER_SCHEDULE` - Schedule for status checks (default: `"6 hours"` - every 6 hours)

**Schedule Formats:**

1. **Cron Expression** (5 fields): `"0 2 * * *"` (minute hour day month day_of_week)
   - Example: `"0 2 * * *"` = Daily at 2:00 AM
   - Example: `"0 9 * * 1-5"` = Weekdays at 9:00 AM
   - Example: `"30 14 * * *"` = Daily at 2:30 PM

2. **Simple Cron** (2 fields): `"hour minute"`
   - Example: `"2 0"` = Daily at 2:00 AM
   - Example: `"8 30"` = Daily at 8:30 AM

3. **Interval**: `"value unit"`
   - Example: `"6 hours"` = Every 6 hours
   - Example: `"30 minutes"` = Every 30 minutes
   - Example: `"60 seconds"` = Every 60 seconds

**Example Configuration (.env.dev):**
```env
JOB_TOKEN_CLEANER_SCHEDULE=0 2 * * *
JOB_DAILY_CHECKLIST_SCHEDULE=0 8 * * *
JOB_STATUS_CHECKER_SCHEDULE=6 hours
```

## Testing

The project is divided into Backend (FastAPI) and Frontend (Angular), each with its own testing suite.

### Backend Testing

The backend includes a comprehensive test suite with unit, integration, and end-to-end (e2e) tests.

#### Test Structure

The test suite is organized into three categories:

1. **Unit Tests** (`tests/test_api/`, `tests/test_utils/`): Test individual functions and components in isolation with mocked dependencies
2. **Integration Tests** (`tests/test_integration/`): Test API endpoints with a real test database
3. **E2E Tests** (`tests/test_e2e/`): Test complete user workflows from start to finish

### Running Tests

#### Using Makefile (Recommended)

```bash

# Run all backend tests (unit + integration + e2e)
make test-backend

# Run only unit tests
make test-backend-unit

# Run only integration tests
make test-backend-integration

# Run only e2e tests
make test-backend-e2e

# Run tests with coverage report
make test-backend-coverage
```

#### Using pytest directly

```bash
cd backend
. venv/bin/activate

# Run all tests
pytest -v

# Run tests by marker
pytest -v -m unit

# Unit tests only
pytest -v -m integration

# Integration tests only
pytest -v -m e2e

# E2E tests only

# Run specific test file
pytest tests/test_api/test_auth_unit.py -v

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term
```

### Test Configuration

Tests use an in-memory SQLite database by default (configured in `tests/conftest.py`). You can override this by setting the `TEST_DATABASE_URL` environment variable:

```bash
export TEST_DATABASE_URL="sqlite:///./test.db"
pytest -v
```

### Writing Tests

#### Unit Tests

Unit tests should mock external dependencies (database, LDAP, etc.) and focus on testing individual functions:

```python
@pytest.mark.unit
class TestAuthUnit:
    @patch('app.api.v1.auth.authenticate_ldap')
    def test_login_success(self, mock_authenticate, db_session):
        mock_authenticate.return_value = True

# Test login logic...
```

#### Integration Tests

Integration tests use a real test database and test API endpoints:

```python
@pytest.mark.integration
class TestAuthIntegration:
    def test_login_flow(self, client, test_db):

# Create test user in database
        user = User(username="testuser", ...)
        test_db.add(user)
        test_db.commit()

# Test API endpoint
        response = client.post("/api/v1/auth/login", ...)
        assert response.status_code == 200
```

#### E2E Tests

E2E tests simulate complete user workflows:

```python
@pytest.mark.e2e
class TestAuthE2E:
    def test_complete_login_and_access_flow(self, client, test_db):

# Step 1: Login
        login_response = client.post("/api/v1/auth/login", ...)

# Step 2: Get user info
        me_response = client.get("/api/v1/auth/me", ...)

# Step 3: Access protected endpoint

# ...
```

### Test Fixtures

The test suite provides several useful fixtures (defined in `tests/conftest.py`):

- `db_session`: Database session for unit tests
- `test_db`: Test database session for integration/e2e tests
- `client`: FastAPI TestClient for synchronous requests
- `async_client`: AsyncClient for asynchronous requests

### Test Markers

Tests are marked with pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests

### Coverage

Generate coverage reports:

```bash

# HTML report (opens in browser)
make test-backend-coverage

# Then open: backend/htmlcov/index.html

# Terminal report
cd backend && pytest --cov=app --cov-report=term
```

## Testing Background Workers

### Overview

All background workers should be thoroughly tested before deployment. The test suite uses **pytest** with async support.

### Running Tests

```bash

# Run all tests
make test-backend

# Run all scheduler and job tests (Unit + Integration + E2E)
make test-jobs

# Run only worker unit tests
cd backend && . venv/bin/activate && pytest tests/test_workers/ -v

# Run specific test file
pytest tests/test_workers/test_token_cleaner.py -v

# Run with coverage
pytest --cov=app.services.workers tests/test_workers/
```

### Writing Tests for Workers

#### Step 1: Create Test File

Create a test file in `backend/tests/test_workers/` (e.g., `test_my_worker.py`):

```python
"""
Tests for MyWorker
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.workers.my_worker import MyWorker


@pytest.mark.asyncio
async def test_my_worker_execution():
    """Test worker executes successfully"""
    worker = MyWorker()

# Mock database session
    with patch.object(worker, 'get_db') as mock_db:
        mock_session = MagicMock()
        mock_db.return_value = mock_session

# Execute worker
        await worker.run()

# Assertions
        assert worker.logger is not None

# Add more assertions based on your worker logic


@pytest.mark.asyncio
async def test_my_worker_error_handling():
    """Test worker handles errors gracefully"""
    worker = MyWorker()
    
    with patch.object(worker, 'get_db') as mock_db:
        mock_db.side_effect = Exception("Database error")

# Should raise exception
        with pytest.raises(Exception):
            await worker.run()


def test_my_worker_name():
    """Test worker has correct name and description"""
    worker = MyWorker()
    assert worker.name == "my_worker"
    assert len(worker.description) > 0
```

#### Step 2: Test Structure

A good worker test should include:

1. **Happy Path Test**: Worker executes successfully
2. **Error Handling Test**: Worker handles errors gracefully
3. **Database Interaction Test**: Worker correctly uses database
4. **Logging Test**: Worker logs important events
5. **Edge Cases**: Test with empty data, null values, etc.

#### Step 3: Common Test Patterns

**Mocking Database:**
```python
with patch.object(worker, 'get_db') as mock_db:
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = []
    mock_session.query.return_value = mock_query
    mock_db.return_value = mock_session
    
    await worker.run()
```

**Testing with Real Data:**
```python
@pytest.mark.asyncio
async def test_worker_with_real_data(db_session):
    """Test worker with real database session"""
    worker = MyWorker()
    worker.db = db_session

# Add test data

# ... create test records
    
    await worker.execute()

# Verify results

# ... check database state
```

**Testing Logging:**
```python
with patch.object(worker.logger, 'info') as mock_info:
    await worker.run()
    assert mock_info.called
    assert "expected log message" in str(mock_info.call_args)
```

**Testing Error Scenarios:**
```python
@pytest.mark.asyncio
async def test_worker_database_error():
    """Test worker handles database errors"""
    worker = MyWorker()
    
    with patch.object(worker, 'get_db') as mock_db:
        mock_db.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            await worker.run()
```
        assert "Connection failed" in str(exc_info.value)
```

#### Step 4: Integration Tests
 
 Verify that your job is correctly registered with the scheduler. Create a test in `backend/tests/test_integration/test_scheduler_integration.py` (or a sidebar file):
 
 ```python
 @pytest.mark.integration
 class TestMyWorkerIntegration:
     def test_job_registration(self):
         from app.services.scheduler import get_scheduler

# Ensure registration logic is called

# register_all_jobs()
         
         sched = get_scheduler()
         job = sched.get_job("my_worker_daily")
         assert job is not None
         assert job.name == "My Daily Worker"
 ```

#### Step 5: End-to-End (E2E) Tests
 
 Verify the job's side effects on the database by running it against a test database. Create a test in `backend/tests/test_e2e/test_jobs_e2e.py`:
 
 ```python
 @pytest.mark.e2e
 class TestJobsE2E:
     @pytest.mark.asyncio
     async def test_my_worker_e2e(self, test_db):
         """
         E2E Test for My Worker.
         1. Seed data
         2. Run worker
         3. Verify side effects
         """

# 1. Seed Data
         user = User(email="active@example.com", is_active=True, ...)
         test_db.add(user)
         test_db.commit()

# 2. Run Job

# Execute the worker directly (bypassing scheduler for immediate feedback)
         worker = MyWorker()

# Optionally pass the test_db session if your worker supports injection

# worker.db = test_db 
         await worker.run()

# 3. Verify Side Effects

# Check logs, database updates, or external service calls (if mocked)

# e.g., verify email was "sent" (mocked service) or DB row updated
 ```

### Test Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (database, APIs, etc.)
3. **Coverage**: Aim for high test coverage (>80%)
4. **Readability**: Use descriptive test names
5. **Speed**: Keep tests fast (use mocks when possible)
6. **Assertions**: Test both success and failure cases
7. **Fixtures**: Use pytest fixtures for common setup

### Example: Complete Test Suite

```python
"""
Complete test suite example for a worker
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.workers.my_worker import MyWorker
from app.models.user import User


class TestMyWorker:
    """Test suite for MyWorker"""
    
    @pytest.mark.asyncio
    async def test_execution_success(self):
        """Test successful execution"""
        worker = MyWorker()
        
        with patch.object(worker, 'get_db') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value = mock_session
            
            result = await worker.run()
            assert result is None

# or check return value
    
    @pytest.mark.asyncio
    async def test_execution_with_data(self):
        """Test execution with test data"""
        worker = MyWorker()
        
        with patch.object(worker, 'get_db') as mock_db:
            mock_session = MagicMock()
            mock_user = Mock(spec=User)
            mock_user.email = "test@example.com"
            
            mock_query = MagicMock()
            mock_query.filter.return_value.all.return_value = [mock_user]
            mock_session.query.return_value = mock_query
            mock_db.return_value = mock_session
            
            await worker.run()

# Verify interactions
            mock_session.query.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling"""
        worker = MyWorker()
        
        with patch.object(worker, 'get_db') as mock_db:
            mock_db.side_effect = Exception("Test error")
            
            with pytest.raises(Exception):
                await worker.run()
    
    def test_worker_attributes(self):
        """Test worker has required attributes"""
        worker = MyWorker()
        assert hasattr(worker, 'name')
        assert hasattr(worker, 'description')
        assert hasattr(worker, 'logger')
        assert worker.name == "my_worker"
```

### Running Tests Before Deployment

```bash

# Run all tests
make test-backend

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app.services.workers --cov-report=html

# Run specific test
pytest tests/test_workers/test_my_worker.py::test_execution_success -v
```

### Continuous Integration

Add to your CI/CD pipeline:

```yaml

# Example GitHub Actions
- name: Run worker tests
  run: |
    cd backend
    pytest tests/test_workers/ -v --cov=app.services.workers
```

## Frontend Testing

The frontend uses **Karma** and **Jasmine** for unit testing.

### Running Tests

```bash

# Run unit tests
make test-frontend

# OR
cd frontend && npm test

# Run with code coverage
cd frontend && ng test --code-coverage
```

### Writing Tests

Tests are co-located with the component/service they test (e.g., `login.component.spec.ts`).

**Example Component Test:**
```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginComponent]
    }).compileComponents();
    
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

## Email Service

The application includes a generic email service for sending emails via SMTP. This service can be used by any worker or API endpoint.

### Configuration

Email service configuration is done via environment variables in `.env.dev`, `.env.staging`, and `.env.prod`:

```env

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=Unified Portal
SMTP_USE_TLS=True
SMTP_USE_SSL=False
SMTP_TIMEOUT=10

# Email Recipients (comma-separated for multiple)
EMAIL_ADMIN_RECIPIENTS=admin@example.com,ops@example.com
EMAIL_ADMIN_CC=manager@example.com
EMAIL_ADMIN_BCC=audit@example.com
```

### Usage

#### Basic Usage

```python
from app.services.email_service import get_email_service

# Get email service instance
email_service = get_email_service()

# Send plain text email
email_service.send_plain_email(
    subject="Test Email",
    text_body="This is a test email.",
    recipients="user@example.com"
)

# Send HTML email
email_service.send_html_email(
    subject="Welcome",
    html_body="<h1>Welcome!</h1><p>Thank you for joining.</p>",
    recipients="user@example.com"
)
```

#### Advanced Usage

```python
from app.services.email_service import get_email_service

email_service = get_email_service()

# Send email with CC and BCC
email_service.send_email(
    subject="Report",
    body="Please find the report attached.",
    recipients="user@example.com",
    cc="manager@example.com",
    bcc="audit@example.com",
    html=False
)

# Send to multiple recipients
email_service.send_email(
    subject="Notification",
    body="Important notification",
    recipients=["user1@example.com", "user2@example.com"],
    cc="team@example.com"
)

# Send HTML email with attachments
attachments = [
    {
        "filename": "report.pdf",
        "content": pdf_file_content

# bytes
    }
]

email_service.send_html_email(
    subject="Monthly Report",
    html_body="<h1>Monthly Report</h1><p>See attachment.</p>",
    recipients="user@example.com",
    attachments=attachments
)
```

#### Using in Workers

**Debug Mode (Development):**
Uses default recipients from environment variables automatically:

```python
from app.services.email_service import get_email_service
from app.core.config import settings

class MyWorker(BaseWorker):
    async def execute(self):

# ... perform work ...

# Send email report (uses EMAIL_ADMIN_RECIPIENTS from env in debug mode)
        email_service = get_email_service()
        email_service.send_html_email_with_defaults(
            subject=f"{settings.APP_NAME} - Daily Report",
            html_body="<h1>Daily Report</h1><p>All systems operational.</p>"

# recipients, cc, bcc are optional in debug mode - uses env defaults
        )
```

**Production Mode:**
Requires explicit recipients (single user or multiple users/DLs):

```python
from app.services.email_service import get_email_service

class MyWorker(BaseWorker):
    async def execute(self):

# ... perform work ...

# Send email with explicit recipients (required in production)
        email_service = get_email_service()
        email_service.send_html_email_with_defaults(
            subject=f"{settings.APP_NAME} - Daily Report",
            html_body="<h1>Daily Report</h1><p>All systems operational.</p>",
            recipients="user@example.com",

# Required in production
            cc="team@example.com",

# Optional
            use_env_defaults=False

# Disable env defaults for production
        )

# Or send to multiple recipients/DLs
        email_service.send_html_email_with_defaults(
            subject="Report",
            html_body="<p>Report content</p>",
            recipients=["user1@example.com", "user2@example.com", "dl-team@example.com"],
            use_env_defaults=False
        )
```

#### Using in API Endpoints

```python
from fastapi import APIRouter
from app.services.email_service import get_email_service

router = APIRouter()

@router.post("/send-notification")
async def send_notification(email: str, message: str):
    email_service = get_email_service()
    success = email_service.send_plain_email(
        subject="Notification",
        text_body=message,
        recipients=email
    )
    return {"success": success}
```

### Environment-Specific Configuration

**Debug Mode (Development/Staging):**
Default recipients are used from environment variables when `DEBUG_MODE=True`:

```env

# .env.dev or .env.staging
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@example.com
SMTP_PASSWORD=dev-password
DEBUG_MODE=True
EMAIL_ADMIN_RECIPIENTS=dev-team@example.com
EMAIL_ADMIN_CC=manager@example.com
EMAIL_ADMIN_BCC=
```

**Production Mode:**
In production (`DEBUG_MODE=False`), recipients must be explicitly provided when sending emails. Environment defaults are ignored for security:

```env

# .env.prod
SMTP_HOST=smtp.production.example.com
SMTP_PORT=587
SMTP_USER=production@example.com
SMTP_PASSWORD=CHANGE_ME_PRODUCTION_PASSWORD
DEBUG_MODE=False

# EMAIL_ADMIN_* are not used in production - recipients must be explicit
```

**Usage Pattern:**

```python

# Debug mode (uses env defaults)
if settings.DEBUG_MODE:
    email_service.send_html_email_with_defaults(
        subject="Report",
        html_body="<p>Content</p>"

# Uses EMAIL_ADMIN_RECIPIENTS from env
    )

# Production mode (requires explicit recipients)
else:
    email_service.send_html_email_with_defaults(
        subject="Report",
        html_body="<p>Content</p>",
        recipients="user@example.com",

# Must be provided
        use_env_defaults=False
    )
```

### SMTP Providers

#### Gmail

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USE_SSL=False
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Use App Password, not regular password
```

**Note**: For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords

#### Outlook/Office 365

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### Custom SMTP Server

```env
SMTP_HOST=mail.example.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=username
SMTP_PASSWORD=password
```

### Email Service Methods

#### `send_email_with_defaults()`

Recommended method that handles debug/production modes automatically:

```python

# Debug mode: Uses EMAIL_ADMIN_RECIPIENTS from env if recipients not provided
email_service.send_email_with_defaults(
    subject="Subject",
    body="Email body",
    recipients=None,

# Uses env default in debug mode
    use_env_defaults=True

# Default: True (uses env defaults in debug mode)
)

# Production mode: Requires explicit recipients
email_service.send_email_with_defaults(
    subject="Subject",
    body="Email body",
    recipients="user@example.com",

# Required in production
    cc="team@example.com",

# Optional
    use_env_defaults=False

# Disable env defaults
)

# Multiple recipients/DLs in production
email_service.send_email_with_defaults(
    subject="Subject",
    body="Email body",
    recipients=["user1@example.com", "user2@example.com", "dl-team@example.com"],
    use_env_defaults=False
)
```

#### `send_email()`

Main method for sending emails with full control (always requires explicit recipients):

```python
email_service.send_email(
    subject="Subject",
    body="Email body",
    recipients="user@example.com",

# or ["user1@example.com", "user2@example.com"]
    cc="cc@example.com",

# optional
    bcc="bcc@example.com",

# optional
    html=True,

# False for plain text
    attachments=[

# optional
        {"filename": "file.pdf", "content": pdf_bytes}
    ]
)
```

#### `send_html_email_with_defaults()`

Convenience method for HTML emails with default recipients support:

```python

# Debug mode: Uses env defaults
email_service.send_html_email_with_defaults(
    subject="HTML Email",
    html_body="<h1>Hello</h1><p>This is HTML.</p>"

# Uses EMAIL_ADMIN_RECIPIENTS from env in debug mode
)

# Production mode: Requires explicit recipients
email_service.send_html_email_with_defaults(
    subject="HTML Email",
    html_body="<h1>Hello</h1><p>This is HTML.</p>",
    recipients="user@example.com",

# Required
    cc="team@example.com",

# Optional
    use_env_defaults=False
)
```

#### `send_plain_email_with_defaults()`

Convenience method for plain text emails with default recipients support:

```python

# Debug mode: Uses env defaults
email_service.send_plain_email_with_defaults(
    subject="Plain Email",
    text_body="This is plain text."

# Uses EMAIL_ADMIN_RECIPIENTS from env in debug mode
)

# Production mode: Requires explicit recipients
email_service.send_plain_email_with_defaults(
    subject="Plain Email",
    text_body="This is plain text.",
    recipients="user@example.com",

# Required
    use_env_defaults=False
)
```

#### `send_html_email()`

Direct method for HTML emails (always requires explicit recipients):

```python
email_service.send_html_email(
    subject="HTML Email",
    html_body="<h1>Hello</h1><p>This is HTML.</p>",
    recipients="user@example.com",
    cc="cc@example.com",
    attachments=[...]
)
```

#### `send_plain_email()`

Direct method for plain text emails (always requires explicit recipients):

```python
email_service.send_plain_email(
    subject="Plain Email",
    text_body="This is plain text.",
    recipients="user@example.com",
    cc="cc@example.com"
)
```

### Error Handling

The email service handles errors gracefully:

```python
email_service = get_email_service()
success = email_service.send_email(...)

if success:
    logger.info("Email sent successfully")
else:
    logger.error("Failed to send email")
```

### Best Practices

1. **Never hardcode credentials**: Always use environment variables
2. **Use App Passwords**: For Gmail, use App Passwords instead of regular passwords
3. **Test in development**: Test email functionality in dev environment first
4. **Handle failures gracefully**: Check return value and log errors
5. **Use HTML templates**: For better formatting, use HTML emails with CSS
6. **Rate limiting**: Be mindful of SMTP rate limits
7. **Error logging**: Email service logs all errors automatically

### Example: Status Checker with Email

The `StatusCheckerWorker` demonstrates email usage:

```python

# In status_checker.py
from app.services.email_service import get_email_service

async def execute(self):

# ... perform checks ...

# Send email report
    email_service = get_email_service()
    email_service.send_html_email(
        subject=f"{settings.APP_NAME} - Status Report",
        html_body=self._build_status_email_html(status_report),
        recipients=settings.EMAIL_ADMIN_RECIPIENTS,
        cc=settings.EMAIL_ADMIN_CC if settings.EMAIL_ADMIN_CC else None
    )
```

## Docker Deployment

The application can be deployed using Docker and Docker Compose for easy setup and consistent environments.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Oracle Database Image

The project uses **`gvenzl/oracle-xe:latest`** for the Oracle database:

**Benefits:**
- âœ… No Oracle Container Registry authentication required
- âœ… Publicly available on Docker Hub
- âœ… Community-maintained and actively updated
- âœ… Same functionality as official Oracle image
- âœ… Automatically creates pluggable database `XEPDB1`
- âœ… Easy to use with simple environment variables

**Configuration:**
- Environment variable: `ORACLE_PASSWORD` (sets password for SYS/SYSTEM users)
- Default pluggable database: `XEPDB1`
- Port: `1521` (standard Oracle port)

### Backend Docker Image - Oracle Instant Client

The backend Docker image uses a **multi-stage build** to install Oracle Instant Client reliably:

**Stage 1 (oracle-client):**
- Uses `oraclelinux:8` as base
- Installs Oracle Instant Client from Oracle's official package repository via `dnf`
- Uses `oracle-instantclient-release-el8` and `oracle-instantclient-basic` packages
- Automatically installs the latest available version (21, 23, etc.)

**Stage 2 (main):**
- Uses `python:3.11-slim` as base
- Copies Oracle Instant Client libraries from stage 1
- Sets up library paths using `ldconfig`
- Includes entrypoint script (`entrypoint.sh`) that:
  - Dynamically detects installed Oracle Instant Client version at runtime
  - Sets `ORACLE_HOME`, `LD_LIBRARY_PATH`, and `PATH` environment variables
  - Ensures `cx_Oracle` can find the libraries regardless of version

**Benefits:**
- âœ… More reliable than direct wget downloads (avoids 404 errors)
- âœ… No authentication issues (uses official Oracle repository)
- âœ… Automatically gets compatible version
- âœ… Smaller final image (only necessary libraries copied)

**If you encounter build errors:**
- The Dockerfile automatically handles Oracle Instant Client installation
- No manual download or setup required
- If build fails, ensure Docker has internet access to Oracle's repository

### Quick Start

```bash

# Build and start all services
make docker-build
make docker-up

# Or use docker-compose directly
docker-compose up -d
```

### Docker Services

The `docker-compose.yml` includes:

1. **Oracle Database** - Oracle XE container
2. **Backend** - FastAPI application
3. **Frontend** - Angular application (production build)
4. **Nginx** - Reverse proxy and load balancer

### Docker Commands

```bash

# Build images
make docker-build

# Start all services
make docker-up

# Start in development mode (with hot reload)
make docker-up-dev

# View logs
make docker-logs
make docker-logs-backend
make docker-logs-frontend
make docker-logs-nginx

# Stop services
make docker-down

# Stop and remove volumes
make docker-down-volumes

# Restart services
make docker-restart

# Rebuild and restart
make docker-rebuild

# Clean up everything
make docker-clean

# Open shell in container
make docker-shell-backend
make docker-shell-frontend
```

### Environment Configuration

Set the environment before starting:

```bash
export ENVIRONMENT=development

# or staging, production
make docker-up
```

Or use docker-compose directly:

```bash
ENVIRONMENT=production docker-compose up -d
```

### Development Mode

For development with hot reload:

```bash

# Start in development mode
make docker-up-dev

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Development mode features:
- Backend: Hot reload with `--reload` flag
- Frontend: Development server with file watching
- Volume mounts for live code changes

### Production Deployment

1. **Set environment variables:**
   ```bash
   export ENVIRONMENT=production
   ```

2. **Update `.env.prod` files:**
   - `backend/.env.prod` - Backend configuration
   - Ensure SMTP, database, and security settings are correct

3. **Build and start:**
   ```bash
   make docker-build
   ENVIRONMENT=production docker-compose up -d
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

### Docker Images

#### Backend Image

- **Base**: `python:3.11-slim` (multi-stage build)
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Features**: Oracle Instant Client, LDAP support
- **Oracle Instant Client Installation**:
  - Uses multi-stage build with `oraclelinux:8`
  - Installs Oracle Instant Client from Oracle's official package repository (auto-detects version: 21, 23, etc.)
  - Copies libraries to Python image (no direct downloads required)
  - Includes entrypoint script (`entrypoint.sh`) that dynamically sets Oracle environment at runtime
  - More reliable than wget-based downloads (avoids 404 errors)
  - Automatically detects and configures the correct Oracle Instant Client version

#### Frontend Image

- **Build Stage**: `node:18-alpine` (multi-stage build)
- **Production Stage**: `nginx:alpine`
- **Port**: 80 (internal), 4200 (mapped)
- **Features**: Optimized production build, gzip compression

#### Nginx Image

- **Base**: `nginx:alpine`
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Features**: Reverse proxy, SSL support, security headers

### Networking

All services are connected via `unified-portal-network`:

- Backend: `http://backend:8000`
- Frontend: `http://frontend:80`
- Oracle: `oracle:1521`

### Volumes

- `oracle-data`: Oracle database data persistence
- `backend-logs`: Backend application logs
- `nginx-logs`: Nginx access and error logs

### Health Checks

All services include health checks:

- **Oracle**: SQL query check
- **Backend**: HTTP `/health` endpoint
- **Frontend**: HTTP GET request
- **Nginx**: HTTP health check

### Troubleshooting

#### Database Connection Issues

**Error**: `ORA-12505: Cannot connect to database. SID XEPDB1 is not registered`

**Solution**: Use the service name format in your connection string:
```env

# Correct format (use ?service_name=)
DATABASE_URL=oracle+cx_oracle://umduser:umd123@localhost:1521/?service_name=XEPDB1

# Incorrect format (don't use /XEPDB1)
DATABASE_URL=oracle+cx_oracle://umduser:umd123@localhost:1521/XEPDB1
```

**Error**: `ORA-01017: invalid username/password; logon denied`

**Solution**: Ensure users are created before running migrations:
```bash

# This will create users if they don't exist
make oracle-create-user

# Or run the full setup which includes user creation
make setup-local-db
```

#### View logs
```bash

# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

#### Check container status
```bash
docker-compose ps
```

#### Restart a service
```bash
docker-compose restart backend
```

#### Rebuild after code changes
```bash

# Rebuild specific service
make docker-rebuild-backend

# Rebuild all
make docker-rebuild
```

#### Database connection issues
```bash

# Check Oracle is healthy
docker-compose ps oracle

# View Oracle logs
docker-compose logs oracle

# Test connection from backend
docker-compose exec backend python -c "from app.core.database import get_engine; print(get_engine())"
```

#### Oracle Instant Client issues in Docker

**Problem**: Backend container can't find Oracle Instant Client libraries

**Solution**: The Dockerfile uses multi-stage build with an entrypoint script that automatically detects and configures Oracle Instant Client. If you see errors:

1. **Rebuild the image:**
   ```bash
   docker-compose build --no-cache backend
   ```

2. **Verify Oracle Instant Client is installed:**
   ```bash
   docker-compose run --rm backend ls -la /usr/lib/oracle/*/client64/lib/
   ```

3. **Check entrypoint script:**
   ```bash
   docker-compose run --rm backend cat /entrypoint.sh
   ```

4. **Verify environment variables are set correctly:**
   ```bash
   docker-compose run --rm backend sh -c "/entrypoint.sh env | grep ORACLE"
   ```

5. **If using local commands without Docker:**
   - Use `make init-db-docker` instead of `make init-db`
   - Use `make migrate-docker` instead of `make migrate`
   - These commands run in Docker containers that have Oracle Instant Client pre-installed
   - The `make oracle-start` command automatically uses Docker-based migrations if local virtual environment is not found

#### Port conflicts
If ports are already in use, modify `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"

# Change 8000 to 8001
```

### Dockerfile Details

#### Backend Dockerfile

- Multi-stage build:
  - Stage 1: Oracle Linux 8 installs Oracle Instant Client via official repository
  - Stage 2: Python 3.11-slim copies libraries and sets up environment
- Includes entrypoint script (`entrypoint.sh`) for dynamic Oracle environment configuration
- Creates non-root user for security
- Includes health check
- Automatically detects Oracle Instant Client version at runtime

#### Frontend Dockerfile

- Multi-stage build:
  - Stage 1: Build Angular app with Node.js
  - Stage 2: Serve with Nginx
- Production optimizations
- Nginx configuration for SPA routing

### SSL/HTTPS Setup

1. Generate SSL certificates (see `nginx/generate-ssl.sh`)
2. Place certificates in `nginx/ssl/`
3. Update `nginx/conf.d/unified-portal.conf` for HTTPS
4. Restart nginx: `docker-compose restart nginx`

### Scaling

Scale services horizontally:

```bash

# Scale backend
docker-compose up -d --scale backend=3

# Scale frontend
Nginx will automatically load balance across instances.

## Error Handling & Logging

The application implements a robust error handling and logging system to ensure visibility and ease of troubleshooting.

### HTTP Status Codes

The API uses standard HTTP status codes to indicate the outcome of requests:

| Status Code | Meaning | Description |
|:

---

:|:

---

|:

---

|
| **200** | OK | Request successful. |
| **201** | Created | Resource successfully created. |
| **400** | Bad Request | Invalid input or validation error. |
| **401** | Unauthorized | Missing or invalid authentication token. |
| **403** | Forbidden | User lacks permission for the resource (RBAC). |
| **404** | Not Found | Resource does not exist. |
| **422** | Unprocessable Entity | Pydantic validation error (invalid schema). |
| **500** | Internal Server Error | Unexpected server error. Full trace logged. |

### Error Response Format

All API errors follow a standard JSON structure:

```json
{
  "detail": "Descriptive error message here"
}
```

For validation errors (422), the structure provides field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Logging & Tracing

The backend uses a centralized middleware (`LoggingMiddleware`) to trace every request.

#### Request IDs
*   Every request is assigned a unique **Trace ID** (`X-Request-ID`).
*   This ID is returned in the response headers.
*   **Debug Tip**: If a user reports an error, ask for the `X-Request-ID` to easily find the relevant logs.

#### Log Format
Logs are structured and include critical context:
```text
TIMESTAMP - middleware - INFO - API Call: METHOD /path - Status: 200
    {
        "request_id": "uuid...",
        "user_id": "123",
        "duration_ms": 45.2,
        "client_ip": "1.2.3.4",
        "user_agent": "Mozilla/..."
    }
```

#### Viewing Logs
*   **Development**: Logs are printed to stdout.
    ```bash
    make run-backend
    ```
*   **Docker**: View container logs.
    ```bash
    docker logs unified-portal-backend
    ```

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review API documentation at `/docs` endpoint
- Contact: [Your Contact Information]
#   u n i f p o r t 
 
 
