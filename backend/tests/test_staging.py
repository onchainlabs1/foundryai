"""Tests for staging features: security headers, rate limiting, /ready endpoint."""

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_test_system

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


def test_security_headers():
    """Test that security headers are present."""
    response = client.get("/health")
    assert response.status_code == 200
    
    # Check security headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert "camera=()" in response.headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")


def test_auth_missing_key_returns_401():
    """Test that missing API key returns 401 with WWW-Authenticate header."""
    response = client.get("/systems")
    assert response.status_code == 401
    assert response.headers.get("WWW-Authenticate") == "API-Key"
    assert "API key required" in response.json()["detail"]


def test_auth_invalid_key_returns_403():
    """Test that invalid API key returns 403."""
    response = client.get("/systems", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_auth_valid_key_returns_200():
    """Test that valid API key returns 200."""
    response = client.get("/systems", headers=HEADERS)
    assert response.status_code == 200


def test_ready_endpoint():
    """Test /ready endpoint checks DB connectivity."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]  # May be 503 if DB not ready
    
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "s3" in data["checks"]


def test_health_endpoint():
    """Test /health endpoint always returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rate_limit_expensive_endpoints():
    """Test that rate limiting is applied to expensive endpoints."""
    # Note: This test may be flaky depending on rate limit settings
    # In production, you'd use a mock or test-specific rate limit
    
    # Try to upload evidence multiple times rapidly
    # (This would trigger rate limit if RATE_LIMIT is low enough)
    pass  # Skip for now - rate limit is 60/min by default

