# Testing Guide

## Quick Start

This guide teaches you how to write tests to achieve 75%+ code coverage.

**See**: [TESTING_GUIDE.md](./TESTING_GUIDE.md) for the complete guide.

## Coverage Requirements

- **Overall**: ≥70%
- **Services**: ≥95%
- **Business Logic**: ≥75%

## Quick Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Validate coverage thresholds
python scripts/validate_coverage.py

# Generate HTML report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Writing Your First Test

```python
import pytest

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestMyAPI:
    def test_endpoint(self, client, regular_token_headers):
        response = client.get("/api/v1/my-endpoint", headers=regular_token_headers)
        assert response.status_code == 200
```

## Common Patterns

### Test API Endpoint
```python
def test_get_items(self, client, regular_token_headers):
    response = client.get("/api/v1/items", headers=regular_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Test with Database
```python
def test_create_item(self, client, admin_token_headers, test_db):
    response = client.post("/api/v1/items", json={"name": "Test"}, headers=admin_token_headers)
    assert response.status_code == 201
```

### Test Error Handling
```python
def test_not_found(self, client, regular_token_headers):
    response = client.get("/api/v1/items/99999", headers=regular_token_headers)
    assert response.status_code == 404
```

## Checking Coverage

```bash
# Check coverage for specific file
pytest tests/test_api_integration/test_my_api.py \
    --cov=app.api.v1.my_api \
    --cov-report=term-missing

# Output shows missing lines:
# app/api/v1/my_api.py    50    5    90%   45-49
#                                           ↑ write tests for these lines
```

## Available Fixtures

- `client` - FastAPI test client
- `regular_token_headers` - Auth headers for regular user
- `admin_token_headers` - Auth headers for admin user
- `test_db` - Test database session
- `regular_user` - Regular user object
- `admin_user` - Admin user object

## Full Documentation

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for:
- Detailed examples
- Integration vs unit tests
- Mocking patterns
- Troubleshooting guide
- Complete code snippets
