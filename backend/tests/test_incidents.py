"""Tests for Incidents endpoints."""

from datetime import datetime, timezone

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


def test_create_incident(setup_test_data):
    """Test creating an incident."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    payload = {
        "system_id": system_id,
        "severity": "medium",
        "description": "Model performance degradation detected",
        "corrective_action": "Investigating root cause"
    }
    response = client.post("/incidents", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "medium"
    assert data["description"] == "Model performance degradation detected"
    assert "id" in data


def test_list_incidents(setup_test_data):
    """Test listing all incidents."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    response = client.get("/incidents", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_incidents_by_system(setup_test_data):
    """Test listing incidents for a specific system."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    response = client.get(f"/incidents?system_id={system_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_incident(setup_test_data):
    """Test updating an incident (resolving it)."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # First create an incident
    create_payload = {
        "system_id": system_id,
        "severity": "low",
        "description": "Test incident"
    }
    create_response = client.post("/incidents", json=create_payload, headers=headers)
    assert create_response.status_code == 200
    incident_id = create_response.json()["id"]
    
    # Now update it - must include all required fields (IncidentCreate schema)
    update_payload = {
        "system_id": system_id,
        "severity": "low",
        "description": "Test incident",
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "corrective_action": "Issue resolved"
    }
    response = client.patch(f"/incidents/{incident_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["corrective_action"] == "Issue resolved"
    assert data["resolved_at"] is not None


def test_create_incident_requires_auth(test_client_with_seed):
    """Test that incident creation requires authentication."""
    client, db_session, org_data = test_client_with_seed
    payload = {"system_id": 1, "severity": "low", "description": "Test"}
    response = client.post("/incidents", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

