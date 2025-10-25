"""Tests for Controls endpoints."""

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


def test_bulk_upsert_controls(setup_test_data):
    """Test bulk upserting controls."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    payload = {
        "controls": [
            {
                "system_id": system_id,
                "iso_clause": "ISO42001:6.1",
                "name": "Risk Management Process",
                "priority": "high",
                "status": "implemented",
                "owner_email": "test@example.com",
                "rationale": "Critical control"
            },
            {
                "system_id": system_id,
                "iso_clause": "ISO42001:7.2",
                "name": "Human Oversight",
                "priority": "medium",
                "status": "partial"
            }
        ]
    }
    response = client.post("/controls/bulk", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "upserted" in data
    assert data["upserted"] == 2


def test_list_system_controls(setup_test_data):
    """Test listing controls for a system."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    response = client.get(f"/systems/{system_id}/controls", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_export_soa_csv(setup_test_data):
    """Test exporting SoA as CSV."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    response = client.get(f"/systems/{system_id}/soa.csv", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    content = response.text
    assert "ISO/IEC 42001 Clause" in content
    assert "Applicable" in content


def test_bulk_upsert_requires_auth(test_client_with_seed):
    """Test that bulk upsert requires authentication."""
    client, db_session, org_data = test_client_with_seed
    payload = {"controls": []}
    response = client.post("/controls/bulk", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

