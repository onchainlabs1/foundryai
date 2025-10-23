"""Tests for FRIA endpoints."""

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_test_system

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def test_create_fria():
    """Test creating a FRIA assessment."""
    # First, create a system
    system_payload = {
        "name": "Test System",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "high"
    }
    system_response = client.post("/systems", json=system_payload, headers=HEADERS)
    assert system_response.status_code == 200
    system_id = system_response.json()["id"]
    
    payload = {
        "system_id": system_id,
        "applicable": True,
        "answers": {
            "biometric_data": "Yes",
            "fundamental_rights": "Yes",
            "critical_infrastructure": "No"
        }
    }
    response = client.post(f"/systems/{system_id}/fria", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["applicable"] is True
    assert data["status"] in ["draft", "submitted", "not_applicable"]
    assert "md_url" in data
    assert "html_url" in data


def test_create_fria_not_applicable():
    """Test creating a FRIA marked as not applicable."""
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
        "applicable": False,
        "answers": {},
        "justification": "System is minimal risk and does not require FRIA"
    }
    response = client.post(f"/systems/{system_id}/fria", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["applicable"] is False
    assert data["status"] == "not_applicable"


def test_get_latest_fria():
    """Test retrieving the latest FRIA for a system."""
    response = client.get("/systems/1/fria/latest", headers=HEADERS)
    # May be 404 if no FRIA exists, or 200 if it does
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "applicable" in data


def test_create_fria_requires_auth():
    """Test that FRIA creation requires authentication."""
    payload = {"system_id": 1, "applicable": True, "answers": {}}
    response = client.post("/systems/1/fria", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

