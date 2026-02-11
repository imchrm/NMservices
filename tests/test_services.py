"""Tests for Services API endpoints."""

import pytest
from fastapi.testclient import TestClient


# --- GET /services Tests (bot, X-API-Key) ---


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


# --- GET /services/{id} Tests (bot, X-API-Key) ---


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


# --- /services write operations removed (security) ---


def test_post_services_not_allowed(client: TestClient, valid_api_key: str):
    """POST /services should return 405 (write ops moved to /admin/services)."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "Should Fail"}
    response = client.post("/services", json=payload, headers=headers)
    assert response.status_code == 405


def test_patch_services_not_allowed(client: TestClient, valid_api_key: str, test_service: int):
    """PATCH /services/{id} should return 405 (write ops moved to /admin/services)."""
    headers = {"X-API-Key": valid_api_key}
    payload = {"name": "Should Fail"}
    response = client.patch(f"/services/{test_service}", json=payload, headers=headers)
    assert response.status_code == 405


def test_delete_services_not_allowed(client: TestClient, valid_api_key: str, test_service: int):
    """DELETE /services/{id} should return 405 (write ops moved to /admin/services)."""
    headers = {"X-API-Key": valid_api_key}
    response = client.delete(f"/services/{test_service}", headers=headers)
    assert response.status_code == 405


# --- Filtering Tests (bot, X-API-Key) ---


def test_get_services_include_inactive(client: TestClient, valid_admin_key: str, valid_api_key: str, test_service: int):
    """Test include_inactive filter."""
    admin_headers = {"X-Admin-Key": valid_admin_key}
    api_headers = {"X-API-Key": valid_api_key}

    # Deactivate the service via admin endpoint
    client.delete(f"/admin/services/{test_service}", headers=admin_headers)

    # Without include_inactive - should be empty
    response = client.get("/services", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service not in service_ids

    # With include_inactive=true - should include the service
    response = client.get("/services?include_inactive=true", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    service_ids = [s["id"] for s in data["services"]]
    assert test_service in service_ids
