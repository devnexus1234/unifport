# Testing Guide: Achieving 75%+ Coverage

## 📚 Table of Contents
1. [Overview](#overview)
2. [Understanding Coverage](#understanding-coverage)
3. [Test Types](#test-types)
4. [Writing Your First Test](#writing-your-first-test)
5. [Integration Tests](#integration-tests)
6. [Unit Tests](#unit-tests)
7. [Running & Validating Tests](#running--validating-tests)
8. [Common Patterns](#common-patterns)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide will teach you how to write tests that achieve 75%+ code coverage for the Unified Portal backend. We use **pytest** for testing and **coverage.py** for measuring coverage.

### Coverage Requirements
- **Overall**: ≥70%
- **Services**: ≥95%
- **Business Logic** (API, models, utils, modules): ≥75%

---

## Understanding Coverage

### What is Code Coverage?

Code coverage measures how much of your code is executed when tests run. For example:

```python
def add(a, b):
    if a < 0:  # Line 2
        return 0  # Line 3 - NOT COVERED if we never test negative numbers
    return a + b  # Line 4
```

**Test with 50% coverage:**
```python
def test_add():
    assert add(5, 3) == 8  # Only tests line 4, not lines 2-3
```

**Test with 100% coverage:**
```python
def test_add_positive():
    assert add(5, 3) == 8  # Tests line 4

def test_add_negative():
    assert add(-1, 3) == 0  # Tests lines 2-3
```

### Checking Coverage

```bash
# Run tests with coverage for a specific file
cd backend
. venv/bin/activate
pytest tests/test_api_integration/test_auth_api.py \
    --cov=app.api.v1.auth \
    --cov-report=term-missing

# Output shows:
# app/api/v1/auth.py    50    5    90%   45-49
#                       ↑     ↑    ↑     ↑
#                    total  missed  %   missing lines
```

---

## Test Types

### 1. Integration Tests
Test entire API endpoints with real HTTP requests.

**Location**: `tests/test_api_integration/`

**Use for**: API endpoints, authentication flows, database interactions

### 2. Unit Tests
Test individual functions in isolation.

**Location**: `tests/test_modules/`, `tests/test_services/`

**Use for**: Utility functions, business logic, services

---

## Writing Your First Test

### Step 1: Create Test File

```bash
# For API endpoint
touch tests/test_api_integration/test_my_api.py

# For service/module
touch tests/test_modules/test_my_module.py
```

### Step 2: Basic Test Structure

```python
"""
Tests for My API
"""
import pytest
from fastapi.testclient import TestClient

# Import fixtures
pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestMyAPI:
    """Test class for My API"""
    
    def test_basic_endpoint(self, client, regular_token_headers):
        """Test description"""
        # Arrange: Set up test data
        test_data = {"name": "test"}
        
        # Act: Make the request
        response = client.get("/api/v1/my-endpoint", headers=regular_token_headers)
        
        # Assert: Check the result
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
```

### Step 3: Run Your Test

```bash
# Run single test
pytest tests/test_api_integration/test_my_api.py::TestMyAPI::test_basic_endpoint -v

# Run with coverage
pytest tests/test_api_integration/test_my_api.py \
    --cov=app.api.v1.my_api \
    --cov-report=term-missing
```

---

## Integration Tests

### Example: Testing an API Endpoint

**File**: `app/api/v1/users.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.api.v1.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Test File**: `tests/test_api_integration/test_users_api.py`
```python
"""
Comprehensive tests for Users API
"""
import pytest
from fastapi.testclient import TestClient
from app.models.user import User

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestUsersAPI:
    """Tests for Users API"""
    
    def test_get_current_user_success(self, client, regular_token_headers, regular_user):
        """Test getting current user info"""
        response = client.get("/api/v1/users/me", headers=regular_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == regular_user.username
        assert data["email"] == regular_user.email
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code in [401, 403]
    
    def test_get_user_by_id_success(self, client, regular_token_headers, test_db):
        """Test getting user by ID"""
        # Create test user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        
        response = client.get(f"/api/v1/users/{user.id}", headers=regular_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_get_user_by_id_not_found(self, client, regular_token_headers):
        """Test getting non-existent user"""
        response = client.get("/api/v1/users/99999", headers=regular_token_headers)
        
        assert response.status_code == 404
```

### Running & Checking Coverage

```bash
# Run tests
pytest tests/test_api_integration/test_users_api.py -v

# Check coverage
pytest tests/test_api_integration/test_users_api.py \
    --cov=app.api.v1.users \
    --cov-report=term-missing

# Expected output:
# app/api/v1/users.py    20    0    100%
```

---

## Unit Tests

### Example: Testing a Utility Function

**File**: `app/utils/validators.py`
```python
def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    if "@" not in email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    if not parts[0] or not parts[1]:
        return False
    return True
```

**Test File**: `tests/test_utils/test_validators.py`
```python
"""
Tests for validators utility
"""
import pytest
from app.utils.validators import validate_email

@pytest.mark.unit
class TestValidators:
    """Tests for validator functions"""
    
    def test_validate_email_valid(self):
        """Test valid email"""
        assert validate_email("user@example.com") == True
    
    def test_validate_email_empty(self):
        """Test empty email"""
        assert validate_email("") == False
    
    def test_validate_email_no_at(self):
        """Test email without @"""
        assert validate_email("userexample.com") == False
    
    def test_validate_email_multiple_at(self):
        """Test email with multiple @"""
        assert validate_email("user@@example.com") == False
    
    def test_validate_email_no_username(self):
        """Test email without username"""
        assert validate_email("@example.com") == False
    
    def test_validate_email_no_domain(self):
        """Test email without domain"""
        assert validate_email("user@") == False
```

### Running Unit Tests

```bash
# Run unit tests
pytest tests/test_utils/test_validators.py -v

# Check coverage
pytest tests/test_utils/test_validators.py \
    --cov=app.utils.validators \
    --cov-report=term-missing

# Expected: 100% coverage
```

---

## Running & Validating Tests

### 1. Run All Tests

```bash
cd backend
. venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

### 2. Run Specific Tests

```bash
# Run single file
pytest tests/test_api_integration/test_auth_api.py

# Run single class
pytest tests/test_api_integration/test_auth_api.py::TestAuthAPI

# Run single test
pytest tests/test_api_integration/test_auth_api.py::TestAuthAPI::test_login_success
```

### 3. Check Coverage for Specific Module

```bash
# Check coverage for auth API
pytest --cov=app.api.v1.auth --cov-report=term-missing

# Check coverage for specific service
pytest --cov=app.services.email_service --cov-report=term-missing
```

### 4. Validate Coverage Thresholds

```bash
# Run validation script
python scripts/validate_coverage.py

# Expected output:
# ✅ Overall Coverage: 84.62% (≥70%)
# ✅ Services: All ≥95%
# ✅ Business Logic: All ≥75%
# ✅ ALL COVERAGE CHECKS PASSED
```

### 5. Generate HTML Coverage Report

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
# firefox htmlcov/index.html
```

The HTML report shows:
- Which lines are covered (green)
- Which lines are not covered (red)
- Exact line numbers to target

---

## Common Patterns

### Pattern 1: Testing with Database

```python
def test_create_item(self, client, admin_token_headers, test_db):
    """Test creating an item"""
    # Create test data
    response = client.post("/api/v1/items", json={
        "name": "Test Item",
        "description": "Test Description"
    }, headers=admin_token_headers)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify in database
    from app.models.item import Item
    item = test_db.query(Item).filter(Item.name == "Test Item").first()
    assert item is not None
    assert item.description == "Test Description"
```

### Pattern 2: Testing Error Handling

```python
def test_create_item_duplicate(self, client, admin_token_headers, test_db):
    """Test creating duplicate item"""
    # Create first item
    item = Item(name="Duplicate", description="First")
    test_db.add(item)
    test_db.commit()
    
    # Try to create duplicate
    response = client.post("/api/v1/items", json={
        "name": "Duplicate",
        "description": "Second"
    }, headers=admin_token_headers)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
```

### Pattern 3: Testing with Mocks

```python
from unittest.mock import patch, MagicMock

def test_send_email(self):
    """Test email sending"""
    with patch('app.services.email_service.smtplib.SMTP') as mock_smtp:
        # Configure mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call function
        from app.services.email_service import send_email
        result = send_email("test@example.com", "Subject", "Body")
        
        # Verify
        assert result == True
        mock_server.send_message.assert_called_once()
```

### Pattern 4: Testing Authentication

```python
def test_endpoint_requires_auth(self, client):
    """Test endpoint requires authentication"""
    response = client.get("/api/v1/protected-endpoint")
    assert response.status_code in [401, 403]

def test_endpoint_requires_admin(self, client, regular_token_headers):
    """Test endpoint requires admin role"""
    response = client.get("/api/v1/admin-endpoint", headers=regular_token_headers)
    assert response.status_code == 403
```

### Pattern 5: Testing Filters/Queries

```python
def test_list_items_with_filter(self, client, regular_token_headers, test_db):
    """Test listing items with filter"""
    # Create test data
    item1 = Item(name="Apple", category="Fruit")
    item2 = Item(name="Banana", category="Fruit")
    item3 = Item(name="Carrot", category="Vegetable")
    test_db.add_all([item1, item2, item3])
    test_db.commit()
    
    # Test filter
    response = client.get("/api/v1/items?category=Fruit", headers=regular_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["category"] == "Fruit" for item in data)
```

---

## Troubleshooting

### Issue 1: Tests Failing with 404

**Problem**: `response.status_code == 404`

**Solution**: Check the API route path
```bash
# Verify routes
python -c "from app.main import app; print([r.path for r in app.routes if 'your-endpoint' in r.path])"
```

### Issue 2: Low Coverage

**Problem**: Coverage is 50% but you have tests

**Solution**: Check which lines are not covered
```bash
# Generate detailed report
pytest --cov=app.api.v1.your_api --cov-report=term-missing

# Look at missing lines:
# app/api/v1/your_api.py    50    25    50%   45-69
#                                              ↑ these lines not covered
```

Then write tests for those specific lines.

### Issue 3: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Ensure you're in the backend directory and virtual environment
```bash
cd backend
. venv/bin/activate
pytest
```

### Issue 4: Database Errors

**Problem**: `sqlalchemy.exc.OperationalError`

**Solution**: Use `test_db` fixture
```python
def test_my_function(self, test_db):  # ← Add test_db
    # Now you can use test_db
    user = User(username="test")
    test_db.add(user)
    test_db.commit()
```

### Issue 5: Authentication Errors

**Problem**: All tests return 401/403

**Solution**: Use authentication fixtures
```python
# Add at top of file
pytest_plugins = ["tests.fixtures.auth_fixtures"]

# Use in test
def test_endpoint(self, client, regular_token_headers):  # ← Add headers
    response = client.get("/api/v1/endpoint", headers=regular_token_headers)
```

---

## Quick Reference

### Available Fixtures

```python
# Client
client              # FastAPI test client

# Authentication
regular_token_headers   # Headers for regular user
admin_token_headers     # Headers for admin user
regular_user            # Regular user object
admin_user              # Admin user object
user_with_role          # User with specific role

# Database
test_db                 # Test database session
```

### Test Markers

```python
@pytest.mark.integration  # Integration test
@pytest.mark.unit         # Unit test
@pytest.mark.slow         # Slow test (skip with -m "not slow")
```

### Common Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# JSON data
data = response.json()
assert "key" in data
assert data["key"] == "value"
assert isinstance(data, list)
assert len(data) > 0

# Database
assert item is not None
assert item.name == "expected"
```

---

## Example: Complete Test File

```python
"""
Comprehensive tests for Items API
"""
import pytest
from fastapi.testclient import TestClient
from app.models.item import Item

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestItemsAPI:
    """Tests for Items API"""
    
    def test_list_items(self, client, regular_token_headers, test_db):
        """Test listing all items"""
        # Create test data
        item1 = Item(name="Item1", description="Desc1")
        item2 = Item(name="Item2", description="Desc2")
        test_db.add_all([item1, item2])
        test_db.commit()
        
        # Make request
        response = client.get("/api/v1/items", headers=regular_token_headers)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_create_item(self, client, admin_token_headers):
        """Test creating an item"""
        response = client.post("/api/v1/items", json={
            "name": "New Item",
            "description": "New Description"
        }, headers=admin_token_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Item"
    
    def test_create_item_unauthorized(self, client, regular_token_headers):
        """Test creating item as non-admin"""
        response = client.post("/api/v1/items", json={
            "name": "Item",
            "description": "Desc"
        }, headers=regular_token_headers)
        
        assert response.status_code == 403
    
    def test_get_item_by_id(self, client, regular_token_headers, test_db):
        """Test getting item by ID"""
        item = Item(name="GetMe", description="Find me")
        test_db.add(item)
        test_db.commit()
        
        response = client.get(f"/api/v1/items/{item.id}", headers=regular_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "GetMe"
    
    def test_get_item_not_found(self, client, regular_token_headers):
        """Test getting non-existent item"""
        response = client.get("/api/v1/items/99999", headers=regular_token_headers)
        
        assert response.status_code == 404
    
    def test_update_item(self, client, admin_token_headers, test_db):
        """Test updating an item"""
        item = Item(name="OldName", description="Old")
        test_db.add(item)
        test_db.commit()
        
        response = client.put(f"/api/v1/items/{item.id}", json={
            "name": "NewName"
        }, headers=admin_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NewName"
    
    def test_delete_item(self, client, admin_token_headers, test_db):
        """Test deleting an item"""
        item = Item(name="DeleteMe", description="Bye")
        test_db.add(item)
        test_db.commit()
        
        response = client.delete(f"/api/v1/items/{item.id}", headers=admin_token_headers)
        
        assert response.status_code == 204
        
        # Verify deletion
        deleted = test_db.query(Item).filter(Item.id == item.id).first()
        assert deleted is None
```

---

## Next Steps

1. **Start Small**: Write tests for one endpoint at a time
2. **Check Coverage**: Run coverage after each test
3. **Target Missing Lines**: Use `--cov-report=term-missing` to find gaps
4. **Iterate**: Add tests until coverage reaches 75%+
5. **Validate**: Run `python scripts/validate_coverage.py`

**Remember**: Good tests are:
- ✅ Clear and readable
- ✅ Test one thing at a time
- ✅ Cover success and error cases
- ✅ Use descriptive names
- ✅ Independent (don't rely on other tests)

Happy testing! 🎉
