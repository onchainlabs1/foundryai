"""Tests for extended Reports endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def test_summary_extended_fields():
    """Test that summary endpoint includes extended fields."""
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


def test_get_score():
    """Test getting compliance scores."""
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


def test_export_deck_pptx():
    """Test exporting executive deck as PPTX."""
    response = client.get("/reports/deck.pptx", headers=HEADERS)
    assert response.status_code == 200
    # Should be a valid file response
    assert "application" in response.headers["content-type"]


def test_export_pptx_alias():
    """Test that /reports/export/pptx redirects to /reports/deck.pptx."""
    response = client.get("/reports/export/pptx", headers=HEADERS, follow_redirects=False)
    assert response.status_code in [200, 307]  # 307 is redirect


def test_export_annex_iv_zip():
    """Test exporting Annex IV package as ZIP."""
    response = client.get("/reports/annex-iv.zip?system_id=1", headers=HEADERS)
    assert response.status_code == 200
    assert "application/zip" in response.headers["content-type"]


def test_score_requires_auth():
    """Test that score endpoint requires authentication."""
    response = client.get("/reports/score")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"

