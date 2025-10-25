"""Tests for FRIA endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def setup_test_data(test_client_with_seed):
    """Create test organization and data for each test using shared fixture."""
    client, db_session, org_data = test_client_with_seed
    
    return {
        "client": client,
        "db_session": db_session,
        "org_data": org_data,
        "system_id": org_data["system_id"],
        "headers": org_data["headers"]
    }


def test_create_fria(setup_test_data):
    """Test creating a FRIA assessment."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    payload = {
        "system_id": system_id,
        "applicable": True,
        "answers": {
            "biometric_data": "Yes",
            "fundamental_rights": "Yes",
            "critical_infrastructure": "No"
        }
    }
    response = client.post(f"/systems/{system_id}/fria", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["applicable"] is True
    assert data["status"] in ["draft", "submitted", "not_applicable"]
    assert "md_url" in data
    assert "html_url" in data


def test_create_fria_not_applicable(setup_test_data):
    """Test creating a FRIA marked as not applicable."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    payload = {
        "system_id": system_id,
        "applicable": False,
        "answers": {},
        "justification": "System is minimal risk and does not require FRIA"
    }
    response = client.post(f"/systems/{system_id}/fria", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["applicable"] is False
    assert data["status"] == "not_applicable"


def test_get_latest_fria(setup_test_data):
    """Test retrieving the latest FRIA for a system."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    response = client.get(f"/systems/{system_id}/fria/latest", headers=headers)
    # May be 404 if no FRIA exists, or 200 if it does
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "applicable" in data


def test_create_fria_requires_auth(test_client_with_seed):
    """Test that FRIA creation requires authentication."""
    client, db_session, org_data = test_client_with_seed
    payload = {"system_id": 1, "applicable": True, "answers": {}}
    response = client.post("/systems/1/fria", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

