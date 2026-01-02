.PHONY: help install-backend install-frontend setup init-db seed-users seed-test-users seed-menus test-rbac run-backend run-frontend run dev clean test lint format migrate docker-build docker-up docker-down docker-logs docker-ps docker-stop docker-restart docker-clean

# Default target
.DEFAULT_GOAL := help

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
PYTHON = python3
PIP = pip3
NPM = npm
VENV = venv

# Oracle XE Container Variables
ORACLE_CONTAINER = unified-portal-oracle
ORACLE_IMAGE = gvenzl/oracle-xe:latest
ORACLE_PORT = 1521
ORACLE_PDB = XEPDB1
ORACLE_USER = umduser
ORACLE_PASSWORD = umd123
ORACLE_SERVICE = XE
ORACLE_HOST = localhost
ORACLE_SCHEMA = umd
TEST_USERNAME = testuser

# Nginx Variables
NGINX_CONTAINER = unified-portal-nginx
NGINX_IMAGE = nginx:alpine
NGINX_HTTP_PORT = 80
NGINX_HTTPS_PORT = 443
NGINX_DIR = nginx
SSL_DIR = $(NGINX_DIR)/ssl

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Unified Portal - Makefile Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Usage Examples:$(NC)"
	@echo "  make setup          # Complete setup (backend + frontend)"
	@echo "  make dev            # Run both backend and frontend"
	@echo "  make run-backend    # Run only backend"
	@echo "  make run-frontend   # Run only frontend"

install-backend: ## Install backend dependencies
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	@echo "$(YELLOW)Installing system dependencies for python-ldap (if needed)...$(NC)"
	@sudo apt-get update -qq > /dev/null 2>&1 && \
	sudo apt-get install -y -qq libldap2-dev libsasl2-dev 2>/dev/null || \
	echo "$(YELLOW)Note: Could not install LDAP dev libraries. python-ldap may not work.$(NC)" || true
	cd $(BACKEND_DIR) && \
	if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi && \
	. $(VENV)/bin/activate && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt || \
	($(PIP) install fastapi uvicorn sqlalchemy cx_Oracle python-jose passlib python-multipart pydantic pydantic-settings alembic && \
	 echo "$(YELLOW)Installed core dependencies. python-ldap skipped (install libldap2-dev if needed).$(NC)")
	@echo "$(GREEN)Backend dependencies installed!$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) install
	@echo "$(GREEN)Frontend dependencies installed!$(NC)"

setup: install-backend install-frontend init-env ## Complete setup (backend + frontend + env)
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Edit backend/.env with your configuration"
	@echo "  2. Run 'make init-db' to initialize database"
	@echo "  3. Run 'make dev' to start development servers"

init-env: ## Initialize environment files
	@echo "$(GREEN)Initializing environment files...$(NC)"
	@if [ ! -f $(BACKEND_DIR)/.env.dev ]; then \
		echo "$(YELLOW)Creating .env.dev...$(NC)"; \
		echo "$(GREEN)Created backend/.env.dev$(NC)"; \
	else \
		echo "$(YELLOW)backend/.env.dev already exists$(NC)"; \
	fi
	@if [ ! -f $(BACKEND_DIR)/.env.staging ]; then \
		echo "$(YELLOW)Creating .env.staging...$(NC)"; \
		echo "$(GREEN)Created backend/.env.staging$(NC)"; \
	else \
		echo "$(YELLOW)backend/.env.staging already exists$(NC)"; \
	fi
	@if [ ! -f $(BACKEND_DIR)/.env.prod ]; then \
		echo "$(YELLOW)Creating .env.prod...$(NC)"; \
		echo "$(GREEN)Created backend/.env.prod$(NC)"; \
	else \
		echo "$(YELLOW)backend/.env.prod already exists$(NC)"; \
	fi
	@echo "$(GREEN)Environment files initialized!$(NC)"
	@echo "$(YELLOW)Note: Update .env.dev, .env.staging, and .env.prod with your specific settings$(NC)"
	@echo "$(YELLOW)Set ENVIRONMENT variable to switch between environments:$(NC)"
	@echo "  - development: Uses .env.dev (default)"
	@echo "  - staging: Uses .env.staging"
	@echo "  - production: Uses .env.prod"

init-db: ## Initialize database with default categories
	@echo "$(GREEN)Initializing database...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/init_db.py

seed-users: ## Seed database with sample users and multiple roles
	@echo "$(GREEN)Seeding users with multiple roles...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/seed_users.py

seed-test-users: ## Seed database with test users for RBAC testing (truncates old data)
	@echo "$(GREEN)Seeding test users for RBAC testing...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/seed_test_users.py

test-rbac: ## Test RBAC permissions for test users
	@echo "$(GREEN)Testing RBAC permissions...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/test_rbac.py
	@echo "$(GREEN)Database initialized!$(NC)"

seed-menus: ## Seed database with default menus, catalogues, and roles
	@echo "$(GREEN)Seeding menus and catalogues...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/seed_menus.py
	@echo "$(GREEN)Menus and catalogues seeded!$(NC)"

init-db-docker: ## Initialize database in Docker container (use when Oracle Instant Client not installed)
	@echo "$(GREEN)Initializing database in Docker container...$(NC)"
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		echo "$(RED)Error: Oracle container is not running$(NC)"; \
		echo "$(YELLOW)Start it with: make oracle-start$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Building backend image if needed...$(NC)"
	@docker-compose build --no-cache backend > /dev/null 2>&1 || docker-compose build backend > /dev/null 2>&1 || true
	@docker-compose run --rm --no-deps \
		-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
		-e ORACLE_HOST=oracle \
		-e ORACLE_USER=$(ORACLE_USER) \
		-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
		-e ORACLE_PORT=1521 \
		-e ORACLE_SERVICE=$(ORACLE_PDB) \
		-e ENVIRONMENT=development \
		backend bash -c "cd /app && python scripts/init_db.py"
	@echo "$(GREEN)Database initialized!$(NC)"

migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	alembic upgrade head
	@echo "$(GREEN)Migrations completed!$(NC)"

migrate-docker: ## Run database migrations in Docker container (use when Oracle Instant Client not installed)
	@echo "$(GREEN)Running database migrations in Docker container...$(NC)"
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		echo "$(RED)Error: Oracle container is not running$(NC)"; \
		echo "$(YELLOW)Start it with: make oracle-start$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Building backend image if needed...$(NC)"
	@docker-compose build --no-cache backend > /dev/null 2>&1 || docker-compose build backend > /dev/null 2>&1 || true
	@docker-compose run --rm --no-deps \
		-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
		-e ORACLE_HOST=oracle \
		-e ORACLE_USER=$(ORACLE_USER) \
		-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
		-e ORACLE_PORT=1521 \
		-e ORACLE_SERVICE=$(ORACLE_PDB) \
		-e ENVIRONMENT=development \
		backend bash -c "cd /app && alembic upgrade head"
	@echo "$(GREEN)Migrations completed!$(NC)"

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Error: MESSAGE is required$(NC)"; \
		echo "Usage: make migrate-create MESSAGE=\"your migration description\""; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating migration: $(MESSAGE)$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	alembic revision --autogenerate -m "$(MESSAGE)"

squash-migrations: ## Squash all migrations (Safe: preserves data)
	@echo "$(YELLOW)This will squash all migrations into a single file.$(NC)"
	@echo "$(YELLOW)It will NOT delete your data.$(NC)"
	@printf "Are you sure? [y/N] " && read ans && \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		echo "$(GREEN)Starting squash process...$(NC)"; \
		cd $(BACKEND_DIR) && \
		. $(VENV)/bin/activate && \
		$(PYTHON) scripts/squash_migrations.py; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

oracle-start: ## Start Oracle XE container
	@echo "$(GREEN)Starting Oracle XE container...$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		if docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
			echo "$(YELLOW)Oracle container already running$(NC)"; \
		else \
			echo "$(GREEN)Starting existing Oracle container...$(NC)"; \
			docker start $(ORACLE_CONTAINER); \
		fi \
	else \
		echo "$(GREEN)Creating and starting Oracle XE container...$(NC)"; \
		docker run -d \
			--name $(ORACLE_CONTAINER) \
			-p $(ORACLE_PORT):1521 \
			-p 5500:5500 \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			$(ORACLE_IMAGE); \
	fi
	@echo "$(YELLOW)Waiting for Oracle to be ready (this may take 1-2 minutes)...$(NC)"
	@timeout=120; \
	while [ $$timeout -gt 0 ]; do \
		if docker exec $(ORACLE_CONTAINER) /bin/bash -c "sqlplus -s / as sysdba <<< 'SELECT 1 FROM DUAL;' > /dev/null 2>&1" 2>/dev/null; then \
			echo "$(GREEN)Oracle is ready!$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		timeout=$$((timeout-2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "$(RED)Oracle failed to start in time$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating users and schemas if not exists...$(NC)"
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_USER) IDENTIFIED BY $(ORACLE_PASSWORD)'';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@echo "$(GREEN)Verifying user '$(ORACLE_USER)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_USER)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ User '$(ORACLE_USER)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for user '$(ORACLE_USER)'$(NC)"; \
		echo "$(YELLOW)  You may need to connect as: $(ORACLE_USER)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)$(NC)"; \
	fi
	@echo "$(GREEN)Creating schema '$(ORACLE_SCHEMA)' if not exists...$(NC)"
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_SCHEMA) IDENTIFIED BY $(ORACLE_PASSWORD)'';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) QUOTA UNLIMITED ON USERS;\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) QUOTA UNLIMITED ON USERS;\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@echo "$(GREEN)Verifying user '$(ORACLE_SCHEMA)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_SCHEMA)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ User '$(ORACLE_SCHEMA)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for user '$(ORACLE_SCHEMA)'$(NC)"; \
		echo "$(YELLOW)  You may need to connect as: $(ORACLE_SCHEMA)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)$(NC)"; \
	fi
	@echo "$(GREEN)Oracle XE container is ready!$(NC)"
	@echo ""
	@echo "$(YELLOW)=== Database Connection Information ===$(NC)"
	@echo "$(GREEN)User: $(ORACLE_USER) | Password: $(ORACLE_PASSWORD) | Schema: $(ORACLE_SCHEMA)$(NC)"
	@echo "$(GREEN)Host: $(ORACLE_HOST) | Port: $(ORACLE_PORT) | Service: $(ORACLE_PDB)$(NC)"
	@echo ""
	@echo "$(YELLOW)Connection String (User: $(ORACLE_USER)):$(NC)"
	@echo "$(GREEN)DATABASE_URL=$(NC)oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)"
	@echo ""
	@echo "$(YELLOW)Connection String (Schema: $(ORACLE_SCHEMA)):$(NC)"
	@echo "$(GREEN)DATABASE_URL=$(NC)oracle+cx_oracle://$(ORACLE_SCHEMA):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)"
	@echo ""
	@echo "$(YELLOW)To use this connection string, export it:$(NC)"
	@echo "export DATABASE_URL=\"oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)\""
	@echo ""
	@echo "$(YELLOW)Running database migrations and initialization...$(NC)"
	@if [ -d "$(VENV)" ]; then \
		echo "$(GREEN)Running database migrations for schema '$(ORACLE_SCHEMA)'...$(NC)"; \
		cd $(BACKEND_DIR) && \
		. $(VENV)/bin/activate && \
		export DATABASE_URL="oracle+cx_oracle://$(ORACLE_SCHEMA):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" && \
		alembic upgrade head && \
		echo "$(GREEN)Migrations completed!$(NC)" && \
		echo "$(GREEN)Initializing database with default data...$(NC)" && \
		$(PYTHON) scripts/init_db.py && \
		echo "$(GREEN)Database initialization completed!$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment not found. Using Docker-based initialization...$(NC)"; \
		echo "$(YELLOW)Building backend image if needed...$(NC)"; \
		docker-compose build --no-cache backend > /dev/null 2>&1 || docker-compose build backend > /dev/null 2>&1 || true; \
		echo "$(YELLOW)Running migrations in Docker container...$(NC)"; \
		docker-compose run --rm --no-deps \
			-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
			-e ORACLE_HOST=oracle \
			-e ORACLE_USER=$(ORACLE_USER) \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			-e ORACLE_PORT=1521 \
			-e ORACLE_SERVICE=$(ORACLE_PDB) \
			-e ENVIRONMENT=development \
			backend sh -c "cd /app && alembic upgrade head" && \
		echo "$(GREEN)Migrations completed!$(NC)" && \
		echo "$(GREEN)Initializing database with default data...$(NC)" && \
		docker-compose run --rm --no-deps \
			-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
			-e ORACLE_HOST=oracle \
			-e ORACLE_USER=$(ORACLE_USER) \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			-e ORACLE_PORT=1521 \
			-e ORACLE_SERVICE=$(ORACLE_PDB) \
			-e ENVIRONMENT=development \
			backend sh -c "cd /app && python scripts/init_db.py" && \
		echo "$(GREEN)Database initialization completed!$(NC)"; \
	fi

oracle-stop: ## Stop Oracle XE container
	@echo "$(GREEN)Stopping Oracle XE container...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		docker stop $(ORACLE_CONTAINER); \
		echo "$(GREEN)Oracle container stopped$(NC)"; \
	else \
		echo "$(YELLOW)Oracle container is not running$(NC)"; \
	fi

oracle-remove: ## Remove Oracle XE container
	@echo "$(RED)Removing Oracle XE container...$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		docker stop $(ORACLE_CONTAINER) 2>/dev/null || true; \
		docker rm $(ORACLE_CONTAINER); \
		echo "$(GREEN)Oracle container removed$(NC)"; \
	else \
		echo "$(YELLOW)Oracle container does not exist$(NC)"; \
	fi

oracle-logs: ## Show Oracle container logs
	@docker logs -f $(ORACLE_CONTAINER) 2>/dev/null || echo "$(YELLOW)Oracle container not found$(NC)"

oracle-create-user: ## Create/update Oracle user (umduser) and schema (umd)
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		echo "$(RED)Error: Oracle container is not running$(NC)"; \
		echo "$(YELLOW)Start it with: make oracle-start$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating user '$(ORACLE_USER)' with password '$(ORACLE_PASSWORD)'...$(NC)"
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_USER) IDENTIFIED BY ''''$(ORACLE_PASSWORD)'''''';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nALTER USER $(ORACLE_USER) DEFAULT TABLESPACE USERS;\nALTER USER $(ORACLE_USER) TEMPORARY TABLESPACE TEMP;\nEXIT;\n' | sqlplus -s / as sysdba" 2>&1 | grep -v "^$$" | grep -v "Session altered" || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nEXIT;\n' | sqlplus -s / as sysdba" 2>&1 | grep -v "^$$" | grep -v "Session altered" || true
	@echo "$(GREEN)Creating schema '$(ORACLE_SCHEMA)' with password '$(ORACLE_PASSWORD)'...$(NC)"
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_SCHEMA) IDENTIFIED BY ''''$(ORACLE_PASSWORD)'''''';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) DEFAULT TABLESPACE USERS;\nALTER USER $(ORACLE_SCHEMA) TEMPORARY TABLESPACE TEMP;\nEXIT;\n' | sqlplus -s / as sysdba" 2>&1 | grep -v "^$$" | grep -v "Session altered" || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) QUOTA UNLIMITED ON USERS;\nEXIT;\n' | sqlplus -s / as sysdba" 2>&1 | grep -v "^$$" | grep -v "Session altered" || true
	@echo "$(GREEN)Verifying user '$(ORACLE_USER)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_USER)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ User '$(ORACLE_USER)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for user '$(ORACLE_USER)'$(NC)"; \
		echo "$(YELLOW)  Try connecting manually: sqlplus $(ORACLE_USER)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)$(NC)"; \
	fi
	@echo "$(GREEN)Verifying schema '$(ORACLE_SCHEMA)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_SCHEMA)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Schema '$(ORACLE_SCHEMA)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for schema '$(ORACLE_SCHEMA)'$(NC)"; \
		echo "$(YELLOW)  Try connecting manually: sqlplus $(ORACLE_SCHEMA)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)$(NC)"; \
	fi
	@echo "$(GREEN)User and schema creation complete!$(NC)"

create-test-user: ## Create initial test user
	@echo "$(GREEN)Creating test user: $(TEST_USERNAME)$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/create_admin.py $(TEST_USERNAME) || echo "$(YELLOW)User may already exist$(NC)"

stop-backend: ## Stop backend server if running
	@echo "$(YELLOW)Stopping backend server...$(NC)"
	@if lsof -ti:8000 > /dev/null 2>&1; then \
		echo "$(GREEN)Found process on port 8000, stopping...$(NC)"; \
		lsof -ti:8000 | xargs kill -9 2>/dev/null || true; \
		echo "$(GREEN)Backend server stopped$(NC)"; \
	else \
		echo "$(YELLOW)No backend server running on port 8000$(NC)"; \
	fi

stop-frontend: ## Stop frontend server if running
	@echo "$(YELLOW)Stopping frontend server...$(NC)"
	@if lsof -ti:4200 > /dev/null 2>&1; then \
		echo "$(GREEN)Found process on port 4200, stopping...$(NC)"; \
		lsof -ti:4200 | xargs kill -9 2>/dev/null || true; \
		echo "$(GREEN)Frontend server stopped$(NC)"; \
	else \
		echo "$(YELLOW)No frontend server running on port 4200$(NC)"; \
	fi
	@if pgrep -f "ng serve\|npm start\|node.*angular" > /dev/null 2>&1; then \
		echo "$(GREEN)Found Angular/Node processes, stopping...$(NC)"; \
		pkill -f "ng serve\|npm start\|node.*angular" 2>/dev/null || true; \
	fi

stop: stop-backend stop-frontend ## Stop both backend and frontend servers

run-backend: stop-backend ## Run backend server (usage: make run-backend ENV=development)
	@echo "$(GREEN)Starting backend server...$(NC)"
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	ENVIRONMENT=$(ENV) $(PYTHON) run.py

run-backend-with-db: oracle-start stop-backend ## Run backend with Oracle database
	@echo "$(GREEN)Starting backend with Oracle database...$(NC)"
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@echo "$(GREEN)Setting up database connection...$(NC)"
	@export DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" && \
	export ORACLE_USER=$(ORACLE_USER) && \
	export ORACLE_PASSWORD=$(ORACLE_PASSWORD) && \
	export ORACLE_HOST=$(ORACLE_HOST) && \
	export ORACLE_PORT=$(ORACLE_PORT) && \
	export ORACLE_SERVICE=$(ORACLE_PDB) && \
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	echo "$(YELLOW)Running database migrations...$(NC)" && \
	alembic upgrade head || echo "$(YELLOW)Migrations may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Initializing database...$(NC)" && \
	$(PYTHON) scripts/init_db.py || echo "$(YELLOW)Database init may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Creating test user...$(NC)" && \
	$(PYTHON) scripts/create_admin.py $(TEST_USERNAME) || echo "$(YELLOW)Test user may already exist$(NC)" && \
	echo "$(GREEN)Starting backend server...$(NC)" && \
	ENVIRONMENT=$(ENV) DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" \
	ORACLE_USER=$(ORACLE_USER) \
	ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
	ORACLE_HOST=$(ORACLE_HOST) \
	ORACLE_PORT=$(ORACLE_PORT) \
	ORACLE_SERVICE=$(ORACLE_PDB) \
	$(PYTHON) run.py

run-frontend: stop-frontend ## Run frontend development server
	@echo "$(GREEN)Starting frontend development server...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) start

dev: stop ## Run both backend and frontend in parallel
	@echo "$(GREEN)Starting development servers...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:4200$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	@trap 'kill 0' EXIT; \
	cd $(BACKEND_DIR) && . $(VENV)/bin/activate && $(PYTHON) run.py & \
	cd $(FRONTEND_DIR) && $(NPM) start & \
	wait

oracle-start-only: ## Start Oracle XE container only (no migrations)
	@echo "$(GREEN)Starting Oracle XE container...$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		if docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
			echo "$(YELLOW)Oracle container already running$(NC)"; \
		else \
			echo "$(GREEN)Starting existing Oracle container...$(NC)"; \
			docker start $(ORACLE_CONTAINER); \
		fi \
	else \
		echo "$(GREEN)Creating and starting Oracle XE container...$(NC)"; \
		docker run -d \
			--name $(ORACLE_CONTAINER) \
			-p $(ORACLE_PORT):1521 \
			-p 5500:5500 \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			$(ORACLE_IMAGE); \
	fi
	@echo "$(YELLOW)Waiting for Oracle to be ready (this may take 1-2 minutes)...$(NC)"
	@timeout=120; \
	while [ $$timeout -gt 0 ]; do \
		if docker exec $(ORACLE_CONTAINER) /bin/bash -c "sqlplus -s / as sysdba <<< 'SELECT 1 FROM DUAL;' > /dev/null 2>&1" 2>/dev/null; then \
			echo "$(GREEN)Oracle is ready!$(NC)"; \
			break; \
		fi; \
		sleep 2; \
		timeout=$$((timeout-2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "$(RED)Oracle failed to start in time$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating users and schemas if not exists...$(NC)"
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_USER) IDENTIFIED BY $(ORACLE_PASSWORD)'';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_USER);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_USER);\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@echo "$(GREEN)Verifying user '$(ORACLE_USER)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_USER)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ User '$(ORACLE_USER)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for user '$(ORACLE_USER)'$(NC)"; \
	fi
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nBEGIN\n  EXECUTE IMMEDIATE ''CREATE USER $(ORACLE_SCHEMA) IDENTIFIED BY $(ORACLE_PASSWORD)'';\n  EXCEPTION WHEN OTHERS THEN\n    IF SQLCODE = -1920 THEN NULL; ELSE RAISE; END IF;\nEND;\n/\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) QUOTA UNLIMITED ON USERS;\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@docker exec $(ORACLE_CONTAINER) /bin/bash -c "printf 'ALTER SESSION SET CONTAINER=$(ORACLE_PDB);\nGRANT CONNECT, RESOURCE, DBA TO $(ORACLE_SCHEMA);\nGRANT UNLIMITED TABLESPACE TO $(ORACLE_SCHEMA);\nALTER USER $(ORACLE_SCHEMA) QUOTA UNLIMITED ON USERS;\nEXIT;\n' | sqlplus -s / as sysdba" > /dev/null 2>&1 || true
	@echo "$(GREEN)Verifying user '$(ORACLE_SCHEMA)' can connect...$(NC)"
	@if docker exec $(ORACLE_CONTAINER) /bin/bash -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s $(ORACLE_SCHEMA)/$(ORACLE_PASSWORD)@$(ORACLE_PDB)" > /dev/null 2>&1; then \
		echo "$(GREEN)✓ User '$(ORACLE_SCHEMA)' verified and can connect$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Warning: Could not verify connection for user '$(ORACLE_SCHEMA)'$(NC)"; \
	fi
	@echo "$(GREEN)Oracle XE container is ready!$(NC)"

setup-local-db: oracle-start-only oracle-create-user ## Setup local database (start Oracle, run migrations, initialize)
	@echo "$(GREEN)Setting up local database...$(NC)"
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@if [ ! -d "$(BACKEND_DIR)/$(VENV)" ]; then \
		echo "$(RED)Error: Virtual environment not found at $(BACKEND_DIR)/$(VENV)$(NC)"; \
		echo "$(YELLOW)Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Checking for Oracle Instant Client...$(NC)"
	@cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	ORACLE_CHECK=$$(python -c "import cx_Oracle; print('OK')" 2>&1); \
	if echo "$$ORACLE_CHECK" | grep -q "DPI-1047\|libclntsh\|libaio\|Cannot locate"; then \
		USE_DOCKER=true; \
		echo "$(YELLOW)Oracle Instant Client not found, will use Docker for migrations$(NC)"; \
	else \
		USE_DOCKER=false; \
		echo "$(GREEN)Oracle Instant Client found, using local migrations$(NC)"; \
	fi; \
	if [ "$$USE_DOCKER" = "false" ]; then \
		echo "$(GREEN)Oracle Instant Client found, running migrations locally...$(NC)"; \
		export DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/?service_name=$(ORACLE_PDB)" && \
		export ORACLE_USER=$(ORACLE_USER) && \
		export ORACLE_PASSWORD=$(ORACLE_PASSWORD) && \
		export ORACLE_HOST=$(ORACLE_HOST) && \
		export ORACLE_PORT=$(ORACLE_PORT) && \
		export ORACLE_SERVICE=$(ORACLE_PDB) && \
		alembic upgrade head && \
		echo "$(GREEN)Migrations completed!$(NC)" && \
		echo "$(YELLOW)Initializing database with default data...$(NC)" && \
		$(PYTHON) scripts/init_db.py && \
		echo "$(GREEN)Database initialized!$(NC)" && \
		echo "$(YELLOW)Creating test user...$(NC)" && \
		$(PYTHON) scripts/create_admin.py $(TEST_USERNAME) || echo "$(YELLOW)Test user may already exist$(NC)"; \
	else \
		echo "$(YELLOW)Oracle Instant Client not found locally, using Docker for migrations...$(NC)"; \
		echo "$(YELLOW)Note: This requires the Docker backend image to be built with libaio fix$(NC)"; \
		echo "$(YELLOW)If migrations fail, rebuild Docker image: docker-compose build --no-cache backend$(NC)"; \
		echo "$(YELLOW)Building backend image if needed...$(NC)"; \
		docker-compose build --no-cache backend > /dev/null 2>&1 || docker-compose build backend > /dev/null 2>&1 || true; \
		echo "$(YELLOW)Running migrations in Docker container...$(NC)"; \
		docker-compose run --rm --no-deps \
			-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
			-e ORACLE_HOST=oracle \
			-e ORACLE_USER=$(ORACLE_USER) \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			-e ORACLE_PORT=1521 \
			-e ORACLE_SERVICE=$(ORACLE_PDB) \
			-e ENVIRONMENT=$(ENV) \
			backend sh -c "cd /app && alembic upgrade head" && \
		echo "$(GREEN)Migrations completed!$(NC)" && \
		echo "$(YELLOW)Initializing database with default data...$(NC)" && \
		docker-compose run --rm --no-deps \
			-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
			-e ORACLE_HOST=oracle \
			-e ORACLE_USER=$(ORACLE_USER) \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			-e ORACLE_PORT=1521 \
			-e ORACLE_SERVICE=$(ORACLE_PDB) \
			-e ENVIRONMENT=$(ENV) \
			backend sh -c "cd /app && python scripts/init_db.py" && \
		echo "$(GREEN)Database initialized!$(NC)" && \
		echo "$(YELLOW)Creating test user...$(NC)" && \
		docker-compose run --rm --no-deps \
			-e DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@oracle:1521/$(ORACLE_PDB)" \
			-e ORACLE_HOST=oracle \
			-e ORACLE_USER=$(ORACLE_USER) \
			-e ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
			-e ORACLE_PORT=1521 \
			-e ORACLE_SERVICE=$(ORACLE_PDB) \
			-e ENVIRONMENT=$(ENV) \
			backend sh -c "cd /app && python scripts/create_admin.py $(TEST_USERNAME)" || echo "$(YELLOW)Test user may already exist$(NC)"; \
	fi
	@echo "$(GREEN)✓ Local database setup complete!$(NC)"
	@echo "$(YELLOW)Database ready at: $(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)$(NC)"

dev-local-backend: stop-backend ## Run backend locally (without Docker, requires setup-local-db first)
	@echo "$(GREEN)Starting backend server locally...$(NC)"
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		echo "$(RED)Error: Oracle container is not running$(NC)"; \
		echo "$(YELLOW)Run: make setup-local-db$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	ENVIRONMENT=$(ENV) \
	DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" \
	ORACLE_USER=$(ORACLE_USER) \
	ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
	ORACLE_HOST=$(ORACLE_HOST) \
	ORACLE_PORT=$(ORACLE_PORT) \
	ORACLE_SERVICE=$(ORACLE_PDB) \
	$(PYTHON) run.py

dev-local-frontend: stop-frontend ## Run frontend locally (without Docker)
	@echo "$(GREEN)Starting frontend development server locally...$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:4200$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) start

dev-local: stop ## Run both backend and frontend locally (without Docker, requires setup-local-db first)
	@echo "$(GREEN)Starting local development servers (BE + FE without Docker)...$(NC)"
	@if ! docker ps --format '{{.Names}}' | grep -q "^$(ORACLE_CONTAINER)$$"; then \
		echo "$(RED)Error: Oracle container is not running$(NC)"; \
		echo "$(YELLOW)Run: make setup-local-db$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:4200$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	@trap 'kill 0' EXIT; \
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	ENVIRONMENT=$(ENV) \
	DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" \
	ORACLE_USER=$(ORACLE_USER) \
	ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
	ORACLE_HOST=$(ORACLE_HOST) \
	ORACLE_PORT=$(ORACLE_PORT) \
	ORACLE_SERVICE=$(ORACLE_PDB) \
	$(PYTHON) run.py & \
	cd $(FRONTEND_DIR) && $(NPM) start & \
	wait

dev-with-db: oracle-start stop ## Run backend with Oracle DB and frontend
	@echo "$(GREEN)Starting development servers with Oracle database...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:4200$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)Oracle: localhost:$(ORACLE_PORT)$(NC)"
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@trap 'kill 0' EXIT; \
	export DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" && \
	export ORACLE_USER=$(ORACLE_USER) && \
	export ORACLE_PASSWORD=$(ORACLE_PASSWORD) && \
	export ORACLE_HOST=$(ORACLE_HOST) && \
	export ORACLE_PORT=$(ORACLE_PORT) && \
	export ORACLE_SERVICE=$(ORACLE_PDB) && \
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	echo "$(YELLOW)Running database migrations...$(NC)" && \
	alembic upgrade head || echo "$(YELLOW)Migrations may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Initializing database...$(NC)" && \
	$(PYTHON) scripts/init_db.py || echo "$(YELLOW)Database init may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Creating test user...$(NC)" && \
	$(PYTHON) scripts/create_admin.py $(TEST_USERNAME) || echo "$(YELLOW)Test user may already exist$(NC)" && \
	echo "$(GREEN)Starting servers...$(NC)" && \
	ENVIRONMENT=$(ENV) DATABASE_URL="oracle+oracledb://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/?service_name=$(ORACLE_PDB)" \
	ORACLE_USER=$(ORACLE_USER) \
	ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
	ORACLE_HOST=$(ORACLE_HOST) \
	ORACLE_PORT=$(ORACLE_PORT) \
	ORACLE_SERVICE=$(ORACLE_PDB) \
	$(PYTHON) run.py & \
	cd $(FRONTEND_DIR) && $(NPM) start & \
	wait

build-backend: ## Build backend for production
	@echo "$(GREEN)Building backend...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Backend build complete!$(NC)"

build-frontend: ## Build frontend for production
	@echo "$(GREEN)Building frontend for production...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run build
	@echo "$(GREEN)Frontend build complete! Output: $(FRONTEND_DIR)/dist/unified-portal$(NC)"

build: build-backend build-frontend ## Build both backend and frontend

test-backend: ## Run all backend tests (unit, integration, e2e)
	@echo "$(GREEN)Running all backend tests...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v

test-backend-unit: ## Run backend unit tests only
	@echo "$(GREEN)Running backend unit tests...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v -m unit

test-backend-integration: ## Run backend integration tests only
	@echo "$(GREEN)Running backend integration tests...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v -m integration

test-backend-e2e: ## Run backend e2e tests only
	@echo "$(GREEN)Running backend e2e tests...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v -m e2e

unit: test-backend-unit ## Alias for test-backend-unit
integration: test-backend-integration ## Alias for test-backend-integration
e2e: test-backend-e2e ## Alias for test-backend-e2e

test-backend-coverage: ## Run backend tests with coverage report
	@echo "$(GREEN)Running backend tests with coverage...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v --cov=app --cov-report=html --cov-report=term

test-jobs: ## Run all scheduler and jobs tests
	@echo "$(GREEN)Running scheduler and jobs tests...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	pytest -v tests/test_services/test_job_registry.py tests/test_services/test_scheduler.py tests/test_workers/ tests/test_integration/test_scheduler_integration.py tests/test_e2e/test_jobs_e2e.py

test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) test

test: test-backend test-frontend ## Run all tests

lint-backend: ## Lint backend code
	@echo "$(GREEN)Linting backend code...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	flake8 app/ || echo "$(YELLOW)flake8 not installed, skipping...$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(GREEN)Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run lint || echo "$(YELLOW)lint script not configured$(NC)"

lint: lint-backend lint-frontend ## Lint all code

format-backend: ## Format backend code
	@echo "$(GREEN)Formatting backend code...$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	black app/ || echo "$(YELLOW)black not installed, skipping...$(NC)"

format-frontend: ## Format frontend code
	@echo "$(GREEN)Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run format || echo "$(YELLOW)format script not configured$(NC)"

format: format-backend format-frontend ## Format all code

clean-backend: ## Clean backend artifacts
	@echo "$(GREEN)Cleaning backend artifacts...$(NC)"
	cd $(BACKEND_DIR) && \
	rm -rf __pycache__ && \
	rm -rf app/__pycache__ && \
	rm -rf app/**/__pycache__ && \
	rm -rf *.pyc && \
	rm -rf .pytest_cache && \
	rm -rf .mypy_cache
	@echo "$(GREEN)Backend cleaned!$(NC)"

clean-frontend: ## Clean frontend artifacts
	@echo "$(GREEN)Cleaning frontend artifacts...$(NC)"
	cd $(FRONTEND_DIR) && \
	rm -rf node_modules && \
	rm -rf dist && \
	rm -rf .angular
	@echo "$(GREEN)Frontend cleaned!$(NC)"

clean-venv: ## Remove backend virtual environment
	@echo "$(GREEN)Removing virtual environment...$(NC)"
	rm -rf $(BACKEND_DIR)/$(VENV)
	@echo "$(GREEN)Virtual environment removed!$(NC)"

clean: clean-backend clean-frontend ## Clean all artifacts

clean-all: clean clean-venv ## Clean everything including virtual environment

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will reset the database!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(BACKEND_DIR) && \
		. $(VENV)/bin/activate && \
		alembic downgrade base && \
		alembic upgrade head && \
		$(PYTHON) scripts/init_db.py; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

check-env: ## Check environment configuration
	@echo "$(GREEN)Checking environment...$(NC)"
	@echo "$(YELLOW)Python:$(NC) $$(which $(PYTHON) || echo 'Not found')"
	@echo "$(YELLOW)Node:$(NC) $$(which node || echo 'Not found')"
	@echo "$(YELLOW)NPM:$(NC) $$(which $(NPM) || echo 'Not found')"
	@if [ -f $(BACKEND_DIR)/.env ]; then \
		echo "$(GREEN)✓ backend/.env exists$(NC)"; \
	else \
		echo "$(RED)✗ backend/.env missing - run 'make init-env'$(NC)"; \
	fi
	@if [ -d $(BACKEND_DIR)/$(VENV) ]; then \
		echo "$(GREEN)✓ Virtual environment exists$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Virtual environment missing - run 'make install-backend'$(NC)"; \
	fi
	@if [ -d $(FRONTEND_DIR)/node_modules ]; then \
		echo "$(GREEN)✓ Frontend dependencies installed$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Frontend dependencies missing - run 'make install-frontend'$(NC)"; \
	fi

logs-backend: ## Show backend logs (if using a process manager)
	@echo "$(YELLOW)Backend logs (if running in background)$(NC)"
	@tail -f $(BACKEND_DIR)/logs/*.log 2>/dev/null || echo "$(YELLOW)No log files found$(NC)"

logs-frontend: ## Show frontend logs
	@echo "$(YELLOW)Frontend logs$(NC)"
	@cd $(FRONTEND_DIR) && $(NPM) run logs 2>/dev/null || echo "$(YELLOW)Logs command not available$(NC)"

status: ## Show status of services
	@echo "$(GREEN)Service Status:$(NC)"
	@echo "$(YELLOW)Oracle:$(NC) $$(docker ps --format '{{.Names}}' | grep -q '^$(ORACLE_CONTAINER)$$' && echo 'Running' || echo 'Not running')"
	@echo "$(YELLOW)Nginx:$(NC) $$(docker ps --format '{{.Names}}' | grep -q '^$(NGINX_CONTAINER)$$' && echo 'Running' || echo 'Not running')"
	@echo "$(YELLOW)Backend:$(NC) $$(curl -s http://localhost:8000/health > /dev/null 2>&1 && echo 'Running' || echo 'Not running')"
	@echo "$(YELLOW)Frontend:$(NC) $$(curl -s http://localhost:4200 > /dev/null 2>&1 && echo 'Running' || echo 'Not running')"
	@if docker ps --format '{{.Names}}' | grep -q '^$(NGINX_CONTAINER)$$'; then \
		echo "$(YELLOW)Nginx URLs:$(NC)"; \
		echo "  HTTP:  http://localhost:$(NGINX_HTTP_PORT)"; \
		echo "  HTTPS: https://localhost:$(NGINX_HTTPS_PORT)"; \
	fi

create-admin: ## Create admin user (usage: make create-admin USERNAME=admin)
	@if [ -z "$(USERNAME)" ]; then \
		echo "$(RED)Error: USERNAME is required$(NC)"; \
		echo "Usage: make create-admin USERNAME=admin"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating admin user: $(USERNAME)$(NC)"
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	$(PYTHON) scripts/create_admin.py $(USERNAME)

# Nginx Commands
nginx-generate-ssl: ## Generate self-signed SSL certificates for local development
	@echo "$(GREEN)Generating SSL certificates...$(NC)"
	@chmod +x $(NGINX_DIR)/generate-ssl.sh
	@$(NGINX_DIR)/generate-ssl.sh
	@echo "$(GREEN)SSL certificates generated in $(SSL_DIR)/$(NC)"

nginx-test: ## Test nginx configuration
	@echo "$(GREEN)Testing nginx configuration...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		docker exec $(NGINX_CONTAINER) nginx -t; \
	else \
		echo "$(YELLOW)Nginx container not running. Testing config file directly...$(NC)"; \
		docker run --rm -v $$(pwd)/$(NGINX_DIR)/nginx.conf:/etc/nginx/nginx.conf:ro \
			-v $$(pwd)/$(NGINX_DIR)/conf.d:/etc/nginx/conf.d:ro \
			$(NGINX_IMAGE) nginx -t; \
	fi

nginx-start: nginx-generate-ssl ## Start nginx container
	@echo "$(GREEN)Starting nginx container...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		echo "$(YELLOW)Nginx container already running$(NC)"; \
	else \
		if docker ps -a --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
			docker start $(NGINX_CONTAINER); \
		else \
			echo "$(YELLOW)Building frontend for nginx...$(NC)"; \
			cd $(FRONTEND_DIR) && $(NPM) run build --configuration=production || echo "$(YELLOW)Frontend build may have failed, continuing...$(NC)"; \
			echo "$(GREEN)Starting nginx with Docker Compose...$(NC)"; \
			cd $(NGINX_DIR) && docker-compose up -d nginx; \
		fi \
	fi
	@echo "$(GREEN)Nginx is running on:$(NC)"
	@echo "  HTTP:  http://localhost:$(NGINX_HTTP_PORT)"
	@echo "  HTTPS: https://localhost:$(NGINX_HTTPS_PORT)"

nginx-stop: ## Stop nginx container
	@echo "$(GREEN)Stopping nginx container...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		docker stop $(NGINX_CONTAINER); \
		echo "$(GREEN)Nginx container stopped$(NC)"; \
	else \
		echo "$(YELLOW)Nginx container is not running$(NC)"; \
	fi

nginx-restart: nginx-stop nginx-start ## Restart nginx container

nginx-reload: ## Reload nginx configuration without restart
	@echo "$(GREEN)Reloading nginx configuration...$(NC)"
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		docker exec $(NGINX_CONTAINER) nginx -s reload; \
		echo "$(GREEN)Nginx configuration reloaded$(NC)"; \
	else \
		echo "$(RED)Error: Nginx container is not running$(NC)"; \
		exit 1; \
	fi

nginx-logs: ## Show nginx logs
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		docker logs -f $(NGINX_CONTAINER); \
	else \
		echo "$(YELLOW)Nginx container not running$(NC)"; \
	fi

nginx-remove: ## Remove nginx container
	@echo "$(RED)Removing nginx container...$(NC)"
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		docker stop $(NGINX_CONTAINER) 2>/dev/null || true; \
		docker rm $(NGINX_CONTAINER); \
		echo "$(GREEN)Nginx container removed$(NC)"; \
	else \
		echo "$(YELLOW)Nginx container does not exist$(NC)"; \
	fi

nginx-dev: ## Run nginx for local development (proxies to local backend/frontend)
	@echo "$(GREEN)Starting nginx for local development...$(NC)"
	@echo "$(YELLOW)Make sure backend (port 8000) and frontend (port 4200) are running$(NC)"
	@if [ ! -f "$(SSL_DIR)/localhost.crt" ] || [ ! -f "$(SSL_DIR)/localhost.key" ]; then \
		$(MAKE) nginx-generate-ssl; \
	fi
	@if docker ps --format '{{.Names}}' | grep -q "^$(NGINX_CONTAINER)$$"; then \
		echo "$(YELLOW)Nginx already running$(NC)"; \
	else \
		echo "$(GREEN)Using development configuration...$(NC)"; \
		if [ -f "$(NGINX_DIR)/conf.d/unified-portal.conf" ] && [ ! -f "$(NGINX_DIR)/conf.d/unified-portal.conf.prod" ]; then \
			mv $(NGINX_DIR)/conf.d/unified-portal.conf $(NGINX_DIR)/conf.d/unified-portal.conf.prod; \
		fi; \
		docker run -d \
			--name $(NGINX_CONTAINER) \
			--network host \
			-v $$(pwd)/$(NGINX_DIR)/nginx.conf:/etc/nginx/nginx.conf:ro \
			-v $$(pwd)/$(NGINX_DIR)/conf.d:/etc/nginx/conf.d:ro \
			-v $$(pwd)/$(SSL_DIR):/etc/nginx/ssl:ro \
			-v $$(pwd)/$(NGINX_DIR)/logs:/var/log/nginx \
			$(NGINX_IMAGE); \
		echo "$(GREEN)Nginx started for local development$(NC)"; \
		echo "  HTTP:  http://localhost:$(NGINX_HTTP_PORT) -> https://localhost:$(NGINX_HTTPS_PORT)"; \
		echo "  HTTPS: https://localhost:$(NGINX_HTTPS_PORT)"; \
		echo "$(YELLOW)Note: Using development config (unified-portal-dev.conf)$(NC)"; \
		echo "$(YELLOW)Note: Browser will show SSL warning for self-signed certificate$(NC)"; \
	fi

dev-with-nginx: oracle-start nginx-dev ## Run full stack with nginx (backend, frontend, nginx)
	@echo "$(GREEN)Starting full stack with nginx...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:4200$(NC)"
	@echo "$(YELLOW)Nginx: https://localhost:$(NGINX_HTTPS_PORT)$(NC)"
	@echo "$(YELLOW)API Docs: https://localhost:$(NGINX_HTTPS_PORT)/api/v1/docs$(NC)"
	@if [ -z "$(ENV)" ]; then \
		ENV=development; \
	fi
	@trap 'kill 0' EXIT; \
	export DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" && \
	export ORACLE_USER=$(ORACLE_USER) && \
	export ORACLE_PASSWORD=$(ORACLE_PASSWORD) && \
	export ORACLE_HOST=$(ORACLE_HOST) && \
	export ORACLE_PORT=$(ORACLE_PORT) && \
	export ORACLE_SERVICE=$(ORACLE_PDB) && \
	cd $(BACKEND_DIR) && \
	. $(VENV)/bin/activate && \
	echo "$(YELLOW)Running database migrations...$(NC)" && \
	alembic upgrade head || echo "$(YELLOW)Migrations may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Initializing database...$(NC)" && \
	$(PYTHON) scripts/init_db.py || echo "$(YELLOW)Database init may have failed, continuing...$(NC)" && \
	echo "$(YELLOW)Creating test user...$(NC)" && \
	$(PYTHON) scripts/create_admin.py $(TEST_USERNAME) || echo "$(YELLOW)Test user may already exist$(NC)" && \
	echo "$(GREEN)Starting backend server...$(NC)" && \
	ENVIRONMENT=$(ENV) DATABASE_URL="oracle+cx_oracle://$(ORACLE_USER):$(ORACLE_PASSWORD)@$(ORACLE_HOST):$(ORACLE_PORT)/$(ORACLE_PDB)" \
	ORACLE_USER=$(ORACLE_USER) \
	ORACLE_PASSWORD=$(ORACLE_PASSWORD) \
	ORACLE_HOST=$(ORACLE_HOST) \
	ORACLE_PORT=$(ORACLE_PORT) \
	ORACLE_SERVICE=$(ORACLE_PDB) \
	$(PYTHON) run.py & \
	cd $(FRONTEND_DIR) && \
	echo "$(GREEN)Starting frontend server...$(NC)" && \
	$(NPM) start & \
	wait

.DEFAULT_GOAL := help

