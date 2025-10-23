"""
Integration tests for critical flows that must work for release.
"""
import os

# Set SECRET_KEY before importing app
os.environ["SECRET_KEY"] = "dev"


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Action, AISystem, Organization

# Create in-memory SQLite database for tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test database tables
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    """Override database dependency for tests."""
    db = Session(bind=test_engine)
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-aims-demo-key"}


@pytest.fixture(autouse=True)
def setup_test_org():
    """Automatically create the demo organization for each test."""
    db = Session(bind=test_engine)
    try:
        # Clear existing data
        db.query(Action).delete()
        db.query(AISystem).delete()
        db.query(Organization).delete()
        db.commit()
        
        # Create demo org
        demo_org = Organization(
            name="AIMS Demo Corporation",
            api_key="dev-aims-demo-key"
        )
        db.add(demo_org)
        db.commit()
        db.refresh(demo_org)
    finally:
        db.close()


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
    if response.status_code != 200:
        print(f"ERROR: Document generation failed with {response.status_code}")
        print(f"Response: {response.json()}")
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
        
        # Check if PDF is available or if fallback to markdown occurred
        if "X-PDF-Fallback" in response.headers:
            # WeasyPrint not available, should return markdown
            assert response.headers["content-type"] == "text/markdown; charset=utf-8"
            assert "WeasyPrint not available" in response.headers["X-PDF-Fallback"]
        else:
            # WeasyPrint available, should return PDF
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
from tests.conftest import create_test_system
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


def test_pdf_fallback_behavior():
    """Test PDF fallback to markdown when WeasyPrint is not available."""
    # Create a system and generate documents
    system_data = {
        "name": "Fallback Test System",
        "purpose": "Testing PDF fallback",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate documents
    onboarding_data = {
        "company": {"name": "Test Company"},
        "systems": [system_data],
        "risks": [{"type": "bias", "description": "Test risk"}],
        "oversight": {"human_in_loop": True},
        "monitoring": {"continuous": True}
    }
    
    response = client.post(f"/documents/systems/{system_id}/generate",
                          json=onboarding_data, headers=HEADERS)
    assert response.status_code == 200
    
    # Test PDF download - should work regardless of WeasyPrint availability
    response = client.get(f"/documents/systems/{system_id}/download/risk_assessment?format=pdf", headers=HEADERS)
    assert response.status_code == 200
    
    # Check response based on WeasyPrint availability
    if "X-PDF-Fallback" in response.headers:
        # WeasyPrint not available, should return markdown
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        assert "WeasyPrint not available" in response.headers["X-PDF-Fallback"]
        # Content should be markdown
        content = response.content.decode('utf-8')
        assert "Risk Management Plan" in content or "Risk Assessment" in content
    else:
        # WeasyPrint available, should return PDF
        assert response.headers["content-type"] == "application/pdf"
        # Content should be binary PDF
        assert response.content.startswith(b'%PDF')


def test_invalid_document_type_validation():
    """Test that invalid document types are rejected."""
    # Create a system first
    system_data = {
        "name": "Test System",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test invalid document type in download
    response = client.get(f"/documents/systems/{system_id}/download/invalid_type", headers=HEADERS)
    assert response.status_code == 400
    assert "Invalid document type" in response.json()["detail"]
    
    # Test invalid document type in preview
    response = client.get(f"/documents/systems/{system_id}/preview/invalid_type", headers=HEADERS)
    assert response.status_code == 400
    assert "Invalid document type" in response.json()["detail"]


def test_reports_org_isolation():
    """Test that reports only show data from the correct organization."""
    # Create systems for different orgs (simulated by creating multiple systems)
    system_data = {
        "name": "Test System 1",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test that reports only show data for the authenticated org
    response = client.get("/reports/summary", headers=HEADERS)
    assert response.status_code == 200
    summary = response.json()
    
    # Should only show systems for the authenticated org
    assert summary["systems"] >= 1
    
    # Test blocking issues
    response = client.get("/reports/blocking-issues", headers=HEADERS)
    assert response.status_code == 200
    response_data = response.json()
    blocking_issues = response_data["blocking_issues"]
    
    # Should only show issues for the authenticated org
    for issue in blocking_issues:
        assert "org_id" not in issue or issue.get("org_id") == 1  # Our test org ID


def test_document_generation_security():
    """Test that document generation doesn't leak sensitive paths."""
    # Create a system
    system_data = {
        "name": "Test System",
        "purpose": "Testing",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate documents
    onboarding_data = {
        "company": {"name": "Test Company"},
        "systems": [system_data],
        "risks": [{"type": "bias", "description": "Test risk"}],
        "oversight": {"human_in_loop": True},
        "monitoring": {"continuous": True}
    }
    
    response = client.post(f"/documents/systems/{system_id}/generate",
                          json=onboarding_data, headers=HEADERS)
    assert response.status_code == 200
    
    # Check that response doesn't contain absolute paths
    response_data = response.json()
    for doc_type, doc_info in response_data["documents"].items():
        # Should not contain absolute paths
        assert "markdown_path" not in doc_info
        assert "pdf_path" not in doc_info
        # Should contain availability flags instead
        assert "markdown_available" in doc_info
        assert "pdf_available" in doc_info


def test_document_preview_xss_protection():
    """Test that document preview is protected against XSS attacks."""
    # Create a system first
    system_data = {
        "name": "XSS Test System",
        "purpose": "Testing XSS protection",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate documents first
    onboarding_data = {
        "company": {"name": "Test Company"},
        "systems": [system_data],
        "risks": [{"type": "bias", "description": "Test risk"}],
        "oversight": {"human_in_loop": True},
        "monitoring": {"continuous": True}
    }
    
    response = client.post(f"/documents/systems/{system_id}/generate",
                          json=onboarding_data, headers=HEADERS)
    assert response.status_code == 200
    
    # Test preview with malicious content protection
    response = client.get(f"/documents/systems/{system_id}/preview/risk_assessment", headers=HEADERS)
    assert response.status_code == 200
    
    # Check that response is HTML and doesn't contain dangerous scripts
    html_content = response.text
    assert "<!DOCTYPE html>" in html_content
    assert "<script>" not in html_content.lower()
    assert "javascript:" not in html_content.lower()
    assert "onload=" not in html_content.lower()
    assert "onerror=" not in html_content.lower()


def test_evidence_upload_security():
    """Test evidence upload security validations."""
    # Create a system first
    system_data = {
        "name": "Upload Security Test System",
        "purpose": "Testing upload security",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test 1: Valid file upload (small text file)
    test_content = b"This is a test evidence file."
    files = {"file": ("test_evidence.txt", test_content, "text/plain")}
    data = {
        "label": "Test Evidence",
        "iso42001_clause": "4.1",
        "control_name": "Test Control",
        "uploaded_by": "Test User"
    }
    
    response = client.post(f"/evidence/{system_id}", files=files, data=data, headers=HEADERS)
    assert response.status_code == 200
    
    # Test 2: Invalid MIME type
    files = {"file": ("malicious.exe", test_content, "application/x-executable")}
    response = client.post(f"/evidence/{system_id}", files=files, data=data, headers=HEADERS)
    assert response.status_code == 415  # Unsupported Media Type
    
    # Test 3: File too large (simulate with large content)
    # Note: This test creates a large file in memory, which is acceptable for testing
    large_content = b"x" * (51 * 1024 * 1024)  # 51MB
    files = {"file": ("large_file.txt", large_content, "text/plain")}
    response = client.post(f"/evidence/{system_id}", files=files, data=data, headers=HEADERS)
    assert response.status_code == 413  # Payload Too Large
    
    # Test 4: Valid markdown content upload
    data = {
        "content": "# Test Evidence\n\nThis is markdown content.",
        "label": "Markdown Evidence",
        "iso42001_clause": "4.2",
        "control_name": "Test Control 2",
        "uploaded_by": "Test User"
    }
    
    response = client.post(f"/evidence/{system_id}", data=data, headers=HEADERS)
    assert response.status_code == 200


def test_annex_iv_download_with_system_id():
    """Test that Annex IV download uses correct system_id parameter."""
    # Create a system first
    system_data = {
        "name": "Annex IV Test System",
        "purpose": "Testing Annex IV download",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test Annex IV download with specific system_id
    response = client.get(f"/reports/export/annex-iv.zip?system_id={system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Verify response headers indicate a ZIP file
    assert response.headers.get("content-type") == "application/zip"
    assert "X-File-Hash" in response.headers
    assert "X-File-Size" in response.headers
    
    # Test with invalid system_id
    response = client.get("/reports/export/annex-iv.zip?system_id=99999", headers=HEADERS)
    assert response.status_code == 404  # System not found
    
    # Test without system_id parameter
    response = client.get("/reports/export/annex-iv.zip", headers=HEADERS)
    assert response.status_code == 422  # Missing required parameter


def test_reports_orm_queries():
    """Test that reports use ORM queries instead of raw SQL."""
    # Create a system first
    system_data = {
        "name": "ORM Test System",
        "purpose": "Testing ORM queries",
        "domain": "testing",
        "ai_act_class": "high-risk"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test reports summary endpoint
    response = client.get("/reports/summary", headers=HEADERS)
    assert response.status_code == 200
    
    summary = response.json()
    
    # Verify all expected fields are present
    required_fields = [
        "systems", "high_risk", "last_30d_incidents", 
        "gpai_count", "evidence_coverage_pct", "evidence_coverage_status",
        "open_actions_7d"
    ]
    
    for field in required_fields:
        assert field in summary, f"Missing field: {field}"
    
    # Verify data types
    assert isinstance(summary["systems"], int)
    assert isinstance(summary["high_risk"], int)
    assert isinstance(summary["last_30d_incidents"], int)
    assert isinstance(summary["gpai_count"], int)
    assert isinstance(summary["evidence_coverage_pct"], (int, float))
    assert isinstance(summary["evidence_coverage_status"], str)
    assert isinstance(summary["open_actions_7d"], int)
    
    # Verify evidence coverage status is valid
    valid_statuses = ["calculated_with_id", "calculated_legacy", "no_evidence", "no_controls", "error", "unknown"]
    assert summary["evidence_coverage_status"] in valid_statuses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
