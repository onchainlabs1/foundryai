"""Tests for Incidents endpoints."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_test_system

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def test_create_incident():
    """Test creating an incident."""
    # First, create a system
    system_payload = {
        "name": "Test System",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "minimal"
    }
    system_response = client.post("/systems", json=system_payload, headers=HEADERS)
    assert system_response.status_code == 200
    system_id = system_response.json()["id"]
    
    payload = {
        "system_id": system_id,
        "severity": "medium",
        "description": "Model performance degradation detected",
        "corrective_action": "Investigating root cause"
    }
    response = client.post("/incidents", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "medium"
    assert data["description"] == "Model performance degradation detected"
    assert "id" in data


def test_list_incidents():
    """Test listing all incidents."""
    response = client.get("/incidents", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_incidents_by_system():
    """Test listing incidents for a specific system."""
    response = client.get("/incidents?system_id=1", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_incident():
    """Test updating an incident (resolving it)."""
    # First, create a system
    system_payload = {
        "name": "Test System",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "minimal"
    }
    system_response = client.post("/systems", json=system_payload, headers=HEADERS)
    assert system_response.status_code == 200
    system_id = system_response.json()["id"]
    
    # First create an incident
    create_payload = {
        "system_id": system_id,
        "severity": "low",
        "description": "Test incident"
    }
    create_response = client.post("/incidents", json=create_payload, headers=HEADERS)
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
    response = client.patch(f"/incidents/{incident_id}", json=update_payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["corrective_action"] == "Issue resolved"
    assert data["resolved_at"] is not None


def test_create_incident_requires_auth():
    """Test that incident creation requires authentication."""
    payload = {"system_id": 1, "severity": "low", "description": "Test"}
    response = client.post("/incidents", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

