"""Tests for Controls endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def test_bulk_upsert_controls():
    """Test bulk upserting controls."""
    payload = {
        "controls": [
            {
                "system_id": 1,
                "iso_clause": "ISO42001:6.1",
                "name": "Risk Management Process",
                "priority": "high",
                "status": "implemented",
                "owner_email": "test@example.com",
                "rationale": "Critical control"
            },
            {
                "system_id": 1,
                "iso_clause": "ISO42001:7.2",
                "name": "Human Oversight",
                "priority": "medium",
                "status": "partial"
            }
        ]
    }
    response = client.post("/controls/bulk", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "upserted" in data
    assert data["upserted"] == 2


def test_list_system_controls():
    """Test listing controls for a system."""
    response = client.get("/systems/1/controls", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_export_soa_csv():
    """Test exporting SoA as CSV."""
    response = client.get("/systems/1/soa.csv", headers=HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    content = response.text
    assert "iso_clause" in content
    assert "applicable" in content


def test_bulk_upsert_requires_auth():
    """Test that bulk upsert requires authentication."""
    payload = {"controls": []}
    response = client.post("/controls/bulk", json=payload)
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

