# Testing Guide for NMservices

## Overview

Tests are configured to use an in-memory SQLite database for fast, isolated testing.

## Setup

1. Install test dependencies:
```bash
poetry install --with dev
```

## Running Tests

### Run all tests:
```bash
poetry run pytest
```

### Run with verbose output:
```bash
poetry run pytest -v
```

### Run specific test file:
```bash
poetry run pytest tests/test_main.py
```

### Run specific test:
```bash
poetry run pytest tests/test_main.py::test_create_order_success
```

### Run with coverage:
```bash
poetry run pytest --cov=nms --cov-report=html
```

## Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
  - `db_session` - Fresh in-memory database for each test
  - `client` - TestClient with database override
  - `valid_api_key` - Valid API key fixture
  - `test_user` - Pre-created test user fixture

- `tests/test_main.py` - API endpoint tests
  - Security tests (authentication)
  - Registration tests
  - Order creation tests (both `/create_order` and `/orders`)
  - Validation error tests

## Test Database

Tests use SQLite in-memory database (`sqlite+aiosqlite:///:memory:`):
- Each test gets a fresh database
- Tables are created before each test
- Tables are dropped after each test
- No persistence between tests
- Fast execution

## Adding New Tests

When adding tests for database operations:

1. Use `db_session` fixture for database access
2. Use `test_user` fixture when you need an existing user
3. Use `client` fixture for API calls
4. Follow the existing test naming convention: `test_<feature>_<scenario>`

Example:
```python
def test_my_feature_success(client: TestClient, valid_api_key: str, test_user: int):
    headers = {"X-API-Key": valid_api_key}
    response = client.post("/my-endpoint", json={"user_id": test_user}, headers=headers)
    assert response.status_code == 200
```
