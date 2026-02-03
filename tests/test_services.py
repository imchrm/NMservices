"""Tests for Services API endpoints."""

import pytest
from fastapi.testclient import TestClient


# --- GET /services Tests ---


def test_get_services_empty(client: TestClient, valid_api_key: str):
    """Get services when no services exist."""
    headers = {"X-API-Key": valid_api_key}
    response = client.get("/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == []
    assert data["total"] == 0


def test_get_services_success(client: TestClient, valid_api_key: str, test_service: int):
    """Get list of active services."""
    headers = {"X-API-Key": valid_api_key}
    response = client.get("/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["services"]) >= 1

    # Check service fields
    service = data["services"][0]
    assert "id" in service
    assert "name" in service
    assert "description" in service
    assert "base_price" in service
    assert "duration_minutes" in service
    assert "is_active" in service


def test_get_services_no_auth(client: TestClient):
    """Get services without API key."""
    response = client.get("/services")
    assert response.status_code == 403


# --- GET /services/{id} Tests ---


def test_get_service_by_id_success(client: TestClient, valid_api_key: str, test_service: int):
    """Get service by ID."""
    headers = {"X-API-Key": valid_api_key}
    response = client.get(f"/services/{test_service}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_service
    assert data["name"] == "Test Massage"
    assert data["is_active"] is True


def test_get_service_by_id_not_found(client: TestClient, valid_api_key: str):
    """Get non-existent service."""
    headers = {"X-API-Key": valid_api_key}
    response = client.get("/services/99999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"


# --- POST /services Tests ---


def test_create_service_success(client: TestClient, valid_api_key: str):
    """Create a new service."""
    headers = {"X-API-Key": valid_api_key}
    payload = {
        "name": "New Massage",
        "description": "A new massage service",
        "base_price": 200000.00,
        "duration_minutes": 90,
        "is_active": True,
    }

    response = client.post("/services", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Massage"
    assert data["description"] == "A new massage service"
    assert float(data["base_price"]) == 200000.00
    assert data["duration_minutes"] == 90
    assert data["is_active"] is True
    assert "id" in data


def test_create_service_minimal(client: TestClient, valid_api_key: str):
    """Create service with only required fields."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "Minimal Service"}

    response = client.post("/services", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Service"
    assert data["description"] is None
    assert data["is_active"] is True  # Default value


def test_create_service_validation_error(client: TestClient, valid_api_key: str):
    """Create service without required name field."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"description": "No name provided"}

    response = client.post("/services", json=payload, headers=headers)

    assert response.status_code == 422  # Validation error


# --- PATCH /services/{id} Tests ---


def test_update_service_success(client: TestClient, valid_api_key: str, test_service: int):
    """Update service fields."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "Updated Massage", "base_price": 180000.00}

    response = client.patch(f"/services/{test_service}", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Massage"
    assert float(data["base_price"]) == 180000.00


def test_update_service_not_found(client: TestClient, valid_api_key: str):
    """Update non-existent service."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "New Name"}

    response = client.patch("/services/99999", json=payload, headers=headers)

    assert response.status_code == 404


# --- DELETE /services/{id} Tests ---


def test_deactivate_service_success(client: TestClient, valid_api_key: str, test_service: int):
    """Deactivate (soft delete) a service."""
    headers = {"X-API-Key": valid_api_key}

    response = client.delete(f"/services/{test_service}", headers=headers)

    assert response.status_code == 204

    # Verify service is deactivated
    get_response = client.get(f"/services/{test_service}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_deactivate_service_not_found(client: TestClient, valid_api_key: str):
    """Deactivate non-existent service."""
    headers = {"X-API-Key": valid_api_key}

    response = client.delete("/services/99999", headers=headers)

    assert response.status_code == 404


# --- Filtering Tests ---


def test_get_services_include_inactive(client: TestClient, valid_api_key: str, test_service: int):
    """Test include_inactive filter."""
    headers = {"X-API-Key": valid_api_key}

    # First deactivate the service
    client.delete(f"/services/{test_service}", headers=headers)

    # Without include_inactive - should be empty
    response = client.get("/services", headers=headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service not in service_ids

    # With include_inactive=true - should include the service
    response = client.get("/services?include_inactive=true", headers=headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service in service_ids
