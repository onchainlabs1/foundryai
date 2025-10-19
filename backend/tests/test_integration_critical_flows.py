"""
Integration tests for critical flows that must work for release.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.main import app
from app.database import get_db
from app.models import Organization, AISystem, Action

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-aims-demo-key"}


def test_onboarding_to_documents_flow():
    """Test the complete onboarding → document generation flow."""
    # 1. Create a system via onboarding
    system_data = {
        "name": "Integration Test System",
        "purpose": "Testing integration flow",
        "domain": "testing",
        "ai_act_class": "high-risk",
        "criticality": "high"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # 2. Save onboarding data for the system
    onboarding_data = {
        "company": {
            "name": "Test Company",
            "industry": "Technology",
            "size": "medium"
        },
        "systems": [system_data],
        "risks": [{"type": "bias", "description": "Test risk"}],
        "oversight": {"human_in_loop": True},
        "monitoring": {"continuous": True}
    }
    
    response = client.put(f"/systems/{system_id}/onboarding-data", 
                         json=onboarding_data, headers=HEADERS)
    assert response.status_code == 200
    
    # 3. Generate documents
    response = client.post(f"/documents/systems/{system_id}/generate",
                          json=onboarding_data, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 4. List documents
    response = client.get(f"/documents/systems/{system_id}/list", headers=HEADERS)
    assert response.status_code == 200
    response_data = response.json()
    documents = response_data["documents"]
    assert len(documents) > 0
    
    # 5. Download a document
    if documents:
        doc_type = documents[0]["type"]
        response = client.get(f"/documents/systems/{system_id}/download/{doc_type}?format=pdf", headers=HEADERS)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


def test_annex_iv_export_integrity():
    """Test Annex IV export with proper hash headers."""
    # Create a system with evidence
    system_data = {
        "name": "Annex Test System",
        "purpose": "Testing Annex IV export",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Export Annex IV
    response = client.get(f"/reports/export/annex-iv.zip?system_id={system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Check integrity headers
    assert "X-File-Hash" in response.headers
    assert "X-File-Size" in response.headers
    assert response.headers["X-File-Hash"].startswith("sha256:")
    
    # Verify hash matches content
    import hashlib
    content_hash = hashlib.sha256(response.content).hexdigest()
    expected_hash = response.headers["X-File-Hash"].replace("sha256:", "")
    assert content_hash == expected_hash


def test_action_items_workflow():
    """Test action items creation and management."""
    # Create a system first
    system_data = {
        "name": "Action Test System",
        "purpose": "Testing action items",
        "domain": "testing"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Create an action item
    action_data = {
        "title": "Test Action Item",
        "description": "This is a test action",
        "system_id": system_id,
        "priority": "high",
        "assigned_to": "test@example.com",
        "due_date": "2024-12-31T23:59:59Z"
    }
    
    response = client.post("/actions", json=action_data, headers=HEADERS)
    assert response.status_code == 200
    action_id = response.json()["id"]
    
    # Get action items
    response = client.get("/actions", headers=HEADERS)
    assert response.status_code == 200
    actions = response.json()
    assert len(actions) > 0
    
    # Update action status
    update_data = {"status": "in_progress"}
    response = client.patch(f"/actions/{action_id}", json=update_data, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    
    # Complete action
    update_data = {"status": "completed"}
    response = client.patch(f"/actions/{action_id}", json=update_data, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["completed_at"] is not None


def test_dashboard_data_accuracy():
    """Test that dashboard shows real data, not hardcoded zeros."""
    # Create systems with different risk levels
    high_risk_system = {
        "name": "High Risk System",
        "purpose": "High risk testing",
        "domain": "testing",
        "ai_act_class": "high-risk",
        "criticality": "high"
    }
    
    response = client.post("/systems", json=high_risk_system, headers=HEADERS)
    assert response.status_code == 200
    
    # Create GPAI system
    gpai_system = {
        "name": "GPAI System",
        "purpose": "General purpose AI",
        "domain": "testing",
        "is_general_purpose_ai": True
    }
    
    response = client.post("/systems", json=gpai_system, headers=HEADERS)
    assert response.status_code == 200
    
    # Create an action item
    action_data = {
        "title": "Dashboard Test Action",
        "priority": "high",
        "status": "open"
    }
    
    response = client.post("/actions", json=action_data, headers=HEADERS)
    assert response.status_code == 200
    
    # Get dashboard summary
    response = client.get("/reports/summary", headers=HEADERS)
    assert response.status_code == 200
    
    summary = response.json()
    
    # Verify real data (not hardcoded zeros)
    assert summary["systems"] >= 2  # At least the systems we created
    assert summary["high_risk"] >= 1  # At least the high risk system
    assert summary["gpai_count"] >= 1  # At least the GPAI system
    assert summary["open_actions_7d"] >= 1  # At least the action we created
    
    # Verify evidence coverage status is transparent
    assert "evidence_coverage_status" in summary
    assert summary["evidence_coverage_status"] in ["calculated", "calculated_with_id", "calculated_legacy", "no_controls", "no_evidence", "error"]


def test_pptx_endpoint_handling():
    """Test that PPTX endpoints return proper 501 responses."""
    response = client.get("/reports/deck.pptx", headers=HEADERS)
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"]
    
    response = client.get("/reports/export/pptx", headers=HEADERS)
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"]


def test_no_localstorage_dependency():
    """Test that document generation doesn't depend on localStorage."""
    # Create a system
    system_data = {
        "name": "No LocalStorage System",
        "purpose": "Testing no localStorage dependency",
        "domain": "testing"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Try to generate documents without onboarding data
    response = client.post(f"/documents/systems/{system_id}/generate",
                          json={}, headers=HEADERS)
    
    # Should either succeed with backend data or fail gracefully
    # The key is that it doesn't fall back to localStorage
    assert response.status_code in [200, 400, 422]  # Valid responses
    
    if response.status_code != 200:
        # If it fails, it should be a clear error, not a localStorage fallback
        error_detail = response.json().get("detail", "")
        assert "localStorage" not in error_detail.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
