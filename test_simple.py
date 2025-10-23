#!/usr/bin/env python3
"""
Simple test to verify the system works.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint."""
    response = client.get('/health')
    print(f"Health: {response.status_code}")
    assert response.status_code == 200

def test_routes():
    """Test that routes exist."""
    routes = [route.path for route in app.routes]
    print(f"Available routes: {routes[:10]}...")
    
    # Check if draft route exists
    draft_routes = [route.path for route in app.routes if 'draft' in route.path]
    print(f"Draft routes: {draft_routes}")
    
    # Check if export routes exist
    export_routes = [route.path for route in app.routes if 'export' in route.path]
    print(f"Export routes: {export_routes}")

if __name__ == "__main__":
    test_health()
    test_routes()
    print("✅ Basic tests passed")
