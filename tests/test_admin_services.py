"""Tests for Admin Services API endpoints (/admin/services)."""

import pytest
from fastapi.testclient import TestClient


# --- Auth Tests ---


def test_admin_services_no_auth(client: TestClient):
    """Admin services endpoints require X-Admin-Key."""
    response = client.get("/admin/services")
    assert response.status_code == 403


def test_admin_services_wrong_key(client: TestClient, valid_api_key: str):
    """Admin services should reject X-API-Key (requires X-Admin-Key)."""
    headers = {"X-API-Key": valid_api_key}
    response = client.get("/admin/services", headers=headers)
    assert response.status_code == 403


# --- GET /admin/services Tests ---


def test_admin_list_services_empty(client: TestClient, valid_admin_key: str):
    """List services when none exist."""
    headers = {"X-Admin-Key": valid_admin_key}
    response = client.get("/admin/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == []
    assert data["total"] == 0


def test_admin_list_services_success(client: TestClient, valid_admin_key: str, test_service: int):
    """List services with existing data."""
    headers = {"X-Admin-Key": valid_admin_key}
    response = client.get("/admin/services", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["services"]) >= 1


def test_admin_list_services_includes_inactive_by_default(client: TestClient, valid_admin_key: str, test_service: int):
    """Admin list includes inactive services by default."""
    headers = {"X-Admin-Key": valid_admin_key}

    # Deactivate the service
    client.delete(f"/admin/services/{test_service}", headers=headers)

    # Default (include_inactive=True) should still show it
    response = client.get("/admin/services", headers=headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service in service_ids

    # Explicit include_inactive=false should hide it
    response = client.get("/admin/services?include_inactive=false", headers=headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service not in service_ids


# --- GET /admin/services/{id} Tests ---


def test_admin_get_service_success(client: TestClient, valid_admin_key: str, test_service: int):
    """Get service by ID via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}
    response = client.get(f"/admin/services/{test_service}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_service
    assert data["name"] == "Test Massage"


def test_admin_get_service_not_found(client: TestClient, valid_admin_key: str):
    """Get non-existent service via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}
    response = client.get("/admin/services/99999", headers=headers)
    assert response.status_code == 404


# --- POST /admin/services Tests ---


def test_admin_create_service_success(client: TestClient, valid_admin_key: str):
    """Create a new service via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}
    payload = {
        "name": "New Massage",
        "description": "A new massage service",
        "base_price": 200000.00,
        "duration_minutes": 90,
        "is_active": True,
    }

    response = client.post("/admin/services", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Massage"
    assert data["description"] == "A new massage service"
    assert float(data["base_price"]) == 200000.00
    assert data["duration_minutes"] == 90
    assert data["is_active"] is True
    assert "id" in data


def test_admin_create_service_minimal(client: TestClient, valid_admin_key: str):
    """Create service with only required fields."""
    headers = {"X-Admin-Key": valid_admin_key}
    payload = {"name": "Minimal Service"}

    response = client.post("/admin/services", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Service"
    assert data["description"] is None
    assert data["is_active"] is True


def test_admin_create_service_validation_error(client: TestClient, valid_admin_key: str):
    """Create service without required name field."""
    headers = {"X-Admin-Key": valid_admin_key}
    payload = {"description": "No name provided"}

    response = client.post("/admin/services", json=payload, headers=headers)
    assert response.status_code == 422


def test_admin_create_service_rejected_with_api_key(client: TestClient, valid_api_key: str):
    """Creating service with X-API-Key should be rejected."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "Should Fail"}

    response = client.post("/admin/services", json=payload, headers=headers)
    assert response.status_code == 403


# --- PATCH /admin/services/{id} Tests ---


def test_admin_update_service_success(client: TestClient, valid_admin_key: str, test_service: int):
    """Update service fields via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}
    payload = {"name": "Updated Massage", "base_price": 180000.00}

    response = client.patch(f"/admin/services/{test_service}", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Massage"
    assert float(data["base_price"]) == 180000.00


def test_admin_update_service_not_found(client: TestClient, valid_admin_key: str):
    """Update non-existent service via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}
    payload = {"name": "New Name"}

    response = client.patch("/admin/services/99999", json=payload, headers=headers)
    assert response.status_code == 404


# --- DELETE /admin/services/{id} Tests ---


def test_admin_deactivate_service_success(client: TestClient, valid_admin_key: str, valid_api_key: str, test_service: int):
    """Deactivate (soft delete) a service via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}

    response = client.delete(f"/admin/services/{test_service}", headers=headers)
    assert response.status_code == 204

    # Verify service is deactivated via bot endpoint
    api_headers = {"X-API-Key": valid_api_key}
    get_response = client.get(f"/services/{test_service}", headers=api_headers)
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_admin_deactivate_service_not_found(client: TestClient, valid_admin_key: str):
    """Deactivate non-existent service via admin endpoint."""
    headers = {"X-Admin-Key": valid_admin_key}

    response = client.delete("/admin/services/99999", headers=headers)
    assert response.status_code == 404
