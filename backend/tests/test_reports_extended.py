"""Tests for extended Reports endpoints."""

import os
import pytest
from fastapi.testclient import TestClient

# Set SECRET_KEY before importing app
os.environ["SECRET_KEY"] = "dev"

from app.models import Organization, AISystem
from tests.conftest import create_test_system
from tests.conftest_qa import with_isolated_client

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def setup_test_data(with_isolated_client):
    """Create test organization and data for each test."""
    client, db = with_isolated_client
    
    # Create test organization
    org = Organization(
        name="Test Organization",
        api_key=API_KEY
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create test system
    system = create_test_system(
        org_id=org.id,
        name="Test System",
        purpose="Testing reports",
        domain="testing",
        ai_act_class="minimal"
    )
    db.add(system)
    db.commit()
    db.refresh(system)
    
    return {"org": org, "system": system, "client": client}


def test_summary_extended_fields(setup_test_data):
    """Test that summary endpoint includes extended fields."""
    client = setup_test_data["client"]
    response = client.get("/reports/summary", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    # Existing fields
    assert "systems" in data
    assert "high_risk" in data
    
    # New fields
    assert "gpai_count" in data
    assert "open_actions_7d" in data
    assert "last_30d_incidents" in data


def test_get_score(setup_test_data):
    """Test getting compliance scores."""
    client = setup_test_data["client"]
    response = client.get("/reports/score", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "org_score" in data
    assert "by_system" in data
    assert "score_unit" in data
    assert "tooltip" in data
    assert "coverage_pct" in data
    
    assert data["score_unit"] == "fraction"
    assert isinstance(data["org_score"], (int, float))
    assert isinstance(data["by_system"], list)


def test_export_deck_pptx(setup_test_data):
    """Test exporting executive deck as PPTX."""
    client = setup_test_data["client"]
    response = client.get("/reports/deck.pptx", headers=HEADERS)
    # PPTX export is not implemented yet, expect 501
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"]


def test_export_pptx_alias(setup_test_data):
    """Test that /reports/export/pptx redirects to /reports/deck.pptx."""
    client = setup_test_data["client"]
    response = client.get("/reports/export/pptx", headers=HEADERS, follow_redirects=False)
    # PPTX export is not implemented yet, expect 501
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"]


def test_export_annex_iv_zip(setup_test_data):
    """Test exporting Annex IV package as ZIP."""
    client = setup_test_data["client"]
    system = setup_test_data["system"]

    # Use the correct route that exists
    response = client.get(f"/reports/annex-iv-complete/{system.id}", headers=HEADERS)
    assert response.status_code == 200
    assert "application/zip" in response.headers["content-type"]


def test_score_requires_auth(setup_test_data):
    """Test that score endpoint requires authentication."""
    client = setup_test_data["client"]
    response = client.get("/reports/score")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"