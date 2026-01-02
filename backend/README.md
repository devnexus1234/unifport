# Unified Portal Backend

FastAPI backend for the Unified Portal application.

## Quick Start

1. **Install system dependencies first** (required for python-ldap):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libldap2-dev libsasl2-dev build-essential python3-dev
# Ensure you are using Python 3.11
# sudo apt-get install python3.11 python3.11-venv python3.11-dev

# macOS
brew install openldap
brew install python@3.11
```

2. **For Oracle connectivity** (if not using Docker):
   - Install Oracle Instant Client from [Oracle Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - Set `LD_LIBRARY_PATH` (Linux) or `PATH` (Windows)
   - **Note**: If you don't have Oracle Instant Client installed locally, use Docker-based commands:
     - `make init-db-docker` instead of `make init-db`
     - `make migrate-docker` instead of `make migrate`
     - The `make oracle-start` command automatically uses Docker-based migrations if local virtual environment is not found

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The `python-ldap` package requires OpenLDAP development headers (`libldap2-dev`, `libsasl2-dev`) to compile. Without these, installation will fail.

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start server:
```bash
python run.py
```

## 📚 Documentation

### Getting Started
- **[Quick Start (Offline)](./QUICK_START_OFFLINE.md)** - Complete offline setup guide
- **[Offline Setup](./OFFLINE_SETUP.md)** - Detailed offline installation instructions

### Testing & Quality
- **[Testing Guide](./TESTING_GUIDE.md)** - Complete guide to writing tests and achieving 75%+ coverage
- **[Testing Quick Reference](./README_TESTING.md)** - Quick commands and patterns for testing
- **[Coverage Validation](./docs/COVERAGE_VALIDATION.md)** - Coverage requirements and validation

### Architecture & Design
- **[RBAC System](./docs/RBAC_SYSTEM.md)** - Role-Based Access Control documentation
- **[Morning Checklist Module](./app/modules/linux/morning_checklist/README.md)** - Morning checklist feature documentation

### Development
- **[Dependencies](./deps/README.md)** - Offline dependencies and package management

---

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Testing

The backend includes comprehensive unit, integration, and e2e tests with **84.62% overall coverage**.

**📖 See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for complete testing documentation.**

### Quick Commands

```bash
# Run all tests
make test-backend

# Run with coverage
make test-backend-coverage

# Validate coverage thresholds (70% overall, 95% services, 75% business logic)
python scripts/validate_coverage.py

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Coverage Requirements
- **Overall**: ≥70% ✅ (Currently: 84.62%)
- **Services**: ≥95% ✅ (All services meet threshold)
- **Business Logic**: ≥75% ✅ (11/11 files meet threshold)

### Quick Test Example

```python
import pytest

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestMyAPI:
    def test_endpoint(self, client, regular_token_headers):
        response = client.get("/api/v1/my-endpoint", headers=regular_token_headers)
        assert response.status_code == 200
```

**For detailed examples, patterns, and troubleshooting**: See [TESTING_GUIDE.md](./TESTING_GUIDE.md)

### Running Tests

```bash
# Run all tests
make test-backend

# Run by category
make test-backend-unit          # Unit tests only
make test-backend-integration   # Integration tests only
make test-backend-e2e          # E2E tests only

# Run with coverage
make test-backend-coverage

# Or use pytest directly
pytest -v                      # All tests
pytest -v -m unit             # Unit tests
pytest -v -m integration       # Integration tests
pytest -v -m e2e              # E2E tests
```

### Test Structure

- **Unit Tests** (`tests/test_api/`, `tests/test_utils/`): Test individual functions with mocked dependencies
- **Integration Tests** (`tests/test_integration/`): Test API endpoints with real test database
- **E2E Tests** (`tests/test_e2e/`): Test complete user workflows

### Test Configuration

Tests use an in-memory SQLite database by default. Override with `TEST_DATABASE_URL`:

```bash
export TEST_DATABASE_URL="sqlite:///./test.db"
pytest -v
```


### Writing Tests

#### 1. Unit Tests
- **Location**: `tests/test_api/` or `tests/test_utils/`
- **Marker**: `@pytest.mark.unit`
- **Fixture**: `client`
- **Focus**: fast, isolated tests with mocked dependencies.

```python
import pytest
from unittest.mock import patch
from fastapi import status

@pytest.mark.unit
def test_example_unit(client):
    # Mock external service or DB call
    with patch("app.services.some_service.get_data", return_value="mocked"):
        response = client.get("/api/v1/resource")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"data": "mocked"}
```

#### 2. Integration Tests
- **Location**: `tests/test_integration/`
- **Marker**: `@pytest.mark.integration`
- **Fixture**: `client` (uses in-memory SQLite)
- **Focus**: API endpoints + Database interactions.

```python
import pytest
from app.models import User

@pytest.mark.integration
def test_example_integration(client, test_db):
    # Setup data
    user = User(username="test", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    
    # Test API interacting with DB
    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == "test"
```

#### 3. E2E Tests
- **Location**: `tests/test_e2e/`
- **Marker**: `@pytest.mark.e2e`
- **Fixture**: `async_client` (for async flows) or `client`
- **Focus**: Full workflows involving multiple steps.

```python
import pytest

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_example_e2e(async_client):
    # 1. Login
    login_res = await async_client.post("/api/v1/login", json={...})
    token = login_res.json()["access_token"]
    
    # 2. Perform authorized action
    headers = {"Authorization": f"Bearer {token}"}
    res = await async_client.get("/api/v1/protected", headers=headers)
    assert res.status_code == 200
```

## RBAC & Visibility

The application uses a simplified Role-Based Access Control (RBAC) model.

### Concepts
- **Roles**: Defined in `roles` table. Assigned to Users.
- **Catalogues**: Functional units/pages.
- **Categories**: Logical grouping of Catalogues.
- **Permissions**: `CatalogueRolePermission` maps a Role to a Catalogue.

### Category Visibility (Implicit)
Categories are **implicitly visible**. A category appears in the side menu if and only if the logged-in user has access to at least one Catalogue within that category. There is no separate permission management for Categories.

### Database Operations

#### Add a New Category
```sql
INSERT INTO catalogue_categories (name, description, icon, display_order, is_active)
VALUES ('NewCategory', 'Description here', 'folder', 10, true);
```

#### Add a New Catalogue
```sql
INSERT INTO catalogues (name, description, category_id, api_endpoint, frontend_route, icon, is_enabled)
VALUES ('MyCatalogue', 'My Desc', (SELECT id FROM catalogue_categories WHERE name='NewCategory'), '/api/v1/mycat', '/mycat', 'description', true);
```

#### Assign Permission
To make a catalogue visible to a user 'jdoe', ensure 'jdoe' has a Role (e.g. 'UserRole'), and then map that Role to the Catalogue:

1. **Find Role ID**: `SELECT id FROM roles WHERE name='UserRole';`
2. **Find Catalogue ID**: `SELECT id FROM catalogues WHERE name='MyCatalogue';`
3. **Insert Permission**:
```sql
INSERT INTO catalogue_role_permissions (catalogue_id, role_id, permission_type)
VALUES (<CATALOGUE_ID>, <ROLE_ID>, 'read');
```
Once this permission is added, 'jdoe' will see 'NewCategory' in the sidebar containing 'MyCatalogue'.
