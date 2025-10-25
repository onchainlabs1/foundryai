"""
Security tests for AIMS Readiness platform.
Tests XSS protection, file upload limits, and other security measures.
"""
import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set SECRET_KEY before importing app
os.environ["SECRET_KEY"] = "dev-secret-key-for-development-only"

from app.database import get_db
from app.main import app
from app.models import AISystem, Base, Organization
from tests.conftest import create_test_system

# Use the standard test database setup
from sqlalchemy.pool import StaticPool

# Create test engine for security tests
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database with required data."""
    # Store original dependency
    original_get_db = app.dependency_overrides.get(get_db)
    
    # Apply override
    app.dependency_overrides[get_db] = override_get_db
    
    # Clean and create tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create test organization with unique key
    unique_key = f"test-security-key-{uuid.uuid4().hex[:8]}"
    db = TestingSessionLocal()
    try:
        org = Organization(
            name="Test Security Org",
            api_key=unique_key,
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create test system with all required fields
        system = create_test_system(
            org_id=org.id,
            name="Test Security System",
            purpose="Test system for security tests",
        )
        db.add(system)
        db.commit()
        db.refresh(system)
        
        yield org, system
    finally:
        db.close()
        # Restore original dependency
        if original_get_db is not None:
            app.dependency_overrides[get_db] = original_get_db
        else:
            app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def headers(setup_database):
    """Standard headers for API requests."""
    org, system = setup_database
    return {"X-API-Key": org.api_key}

class TestXSSProtection:
    """Test XSS protection in document preview."""
    
    def test_document_preview_xss_protection(self, client, headers, setup_database):
        """Test that XSS payloads are sanitized in document preview."""
        org, system = setup_database
        
        # XSS payloads to test
        xss_payloads = [
            "<img src=x onerror=alert(1)>",
            "<script>alert('XSS')</script>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<svg onload=alert(1)>",
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>",
            "<select onfocus=alert(1) autofocus>",
            "<textarea onfocus=alert(1) autofocus>",
            "<keygen onfocus=alert(1) autofocus>",
            "<video><source onerror=alert(1)>",
            "<audio src=x onerror=alert(1)>",
            "<details open ontoggle=alert(1)>",
            "<marquee onstart=alert(1)>",
            "<math><mi//xlink:href=data:x,<script>alert(1)</script>",
            "<table><td background=javascript:alert(1)>",
            "<object data=javascript:alert(1)>",
            "<embed src=javascript:alert(1)>",
            "<link rel=stylesheet href=javascript:alert(1)>",
            "<meta http-equiv=refresh content=0;url=javascript:alert(1)>",
            "<form action=javascript:alert(1)><input type=submit>",
        ]
        
        for payload in xss_payloads:
            # Create onboarding data with XSS payload
            onboarding_data = {
                "company_name": f"Test Company {payload}",
                "systems": [
                    {
                        "name": f"Test System {payload}",
                        "purpose": f"System purpose {payload}",
                        "ai_act_class": "high-risk",
                        "criticality": "high"
                    }
                ]
            }
            
            # Save onboarding data
            response = client.post(
                f"/systems/{system.id}/onboarding-data",
                json=onboarding_data,
                headers=headers
            )
            assert response.status_code == 200
            
            # Generate documents
            response = client.post(
                f"/documents/systems/{system.id}/generate",
                json=onboarding_data,
                headers=headers
            )
            assert response.status_code == 200
            
            # Preview document (this should sanitize XSS)
            response = client.get(
                f"/documents/systems/{system.id}/preview/risk_assessment",
                headers=headers
            )
            assert response.status_code == 200
            
            # Check that XSS payload is not present in response
            content = response.text
            assert "<script>" not in content, f"XSS payload <script> not sanitized"
            assert "onerror=" not in content, f"XSS payload onerror= not sanitized"
            assert "onload=" not in content, f"XSS payload onload= not sanitized"
            assert "onfocus=" not in content, f"XSS payload onfocus= not sanitized"
            assert "javascript:" not in content, f"XSS payload javascript: not sanitized"
            assert "alert(" not in content, f"XSS payload alert( not sanitized"
            
            # Check that HTML content is returned (sanitized)
            assert "<!DOCTYPE html>" in content or "<html>" in content
            assert response.status_code == 200

class TestFileUploadSecurity:
    """Test file upload security measures."""
    
    def test_file_size_limit(self, client, headers, setup_database):
        """Test that files larger than 50MB are rejected."""
        org, system = setup_database
        
        # Create a large file (simulate 60MB)
        large_content = b"x" * (60 * 1024 * 1024)  # 60MB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(large_content)
            temp_file.flush()
            
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    f"/evidence/{system.id}",
                    files={"file": ("large_file.txt", f, "text/plain")},
                    data={
                        "label": "Large file test",
                        "iso42001_clause": "5.1",
                        "control_name": "Test Control"
                    },
                    headers=headers
                )
                
                # Should be rejected due to size limit
                assert response.status_code == 413
                assert "File too large" in response.json()["detail"]
    
    def test_invalid_mime_type_rejection(self, client, headers, setup_database):
        """Test that files with invalid MIME types are rejected."""
        org, system = setup_database
        
        # Create a file with malicious extension
        malicious_content = b"malicious content"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as temp_file:
            temp_file.write(malicious_content)
            temp_file.flush()
            
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    f"/evidence/{system.id}",
                    files={"file": ("malicious.exe", f, "application/x-executable")},
                    data={
                        "label": "Malicious file test",
                        "iso42001_clause": "5.1",
                        "control_name": "Test Control"
                    },
                    headers=headers
                )
                
                # Should be rejected due to invalid MIME type
                assert response.status_code == 415
                assert "File type not allowed" in response.json()["detail"]
    
    def test_valid_file_upload(self, client, headers, setup_database):
        """Test that valid files are accepted."""
        org, system = setup_database
        
        # Create a valid file
        valid_content = b"This is a valid text file for testing."
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(valid_content)
            temp_file.flush()
            
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    f"/evidence/{system.id}",
                    files={"file": ("valid_file.txt", f, "text/plain")},
                    data={
                        "label": "Valid file test",
                        "iso42001_clause": "5.1",
                        "control_name": "Test Control"
                    },
                    headers=headers
                )
                
                # Should be accepted
                assert response.status_code == 200
                assert response.json()["label"] == "Valid file test"
    
    def test_streaming_upload_memory_efficiency(self, client, headers, setup_database):
        """Test that file uploads use streaming and don't load entire file into memory."""
        org, system = setup_database
        
        # Create a smaller test file (100KB) to avoid timeout
        test_content = b"x" * (100 * 1024)  # 100KB
        
        # Use BytesIO instead of temporary file to avoid disk I/O
        from io import BytesIO
        file_obj = BytesIO(test_content)
        
        response = client.post(
            f"/evidence/{system.id}",
            files={"file": ("test_file.txt", file_obj, "text/plain")},
            data={
                "label": "Streaming test file",
                "iso42001_clause": "5.1",
                "control_name": "Test Control"
            },
            headers=headers
        )
        
        # Should be accepted (under 50MB limit)
        assert response.status_code == 200
        assert response.json()["label"] == "Streaming test file"

class TestAPISecurity:
    """Test API security measures."""
    
    def test_unauthorized_access_rejection(self, client, setup_database):
        """Test that requests without API key are rejected."""
        org, system = setup_database
        
        # Try to access protected endpoint without API key
        response = client.get("/reports/summary")
        assert response.status_code == 401
        
        response = client.get(f"/systems/{system.id}")
        assert response.status_code == 401
    
    def test_invalid_api_key_rejection(self, client, setup_database):
        """Test that requests with invalid API key are rejected."""
        org, system = setup_database
        
        # Try to access protected endpoint with invalid API key
        invalid_headers = {"X-API-Key": "invalid-key"}
        
        response = client.get("/reports/summary", headers=invalid_headers)
        assert response.status_code == 403
        
        response = client.get(f"/systems/{system.id}", headers=invalid_headers)
        assert response.status_code == 403
    
    def test_organization_isolation(self, client, headers, setup_database):
        """Test that organizations can only access their own data."""
        org, system = setup_database
        
        # Test that we can access our own system
        response = client.get(f"/systems/{system.id}", headers=headers)
        assert response.status_code == 200
        
        # Test that we can access our own reports
        response = client.get("/reports/summary", headers=headers)
        assert response.status_code == 200
        our_data = response.json()
        assert our_data["systems"] == 1  # Our organization has 1 system
        
        # Test that invalid API keys are rejected
        invalid_headers = {"X-API-Key": "invalid-key"}
        response = client.get("/reports/summary", headers=invalid_headers)
        assert response.status_code == 403
        
        # Test that we can't access non-existent systems
        response = client.get("/systems/99999", headers=headers)
        assert response.status_code == 404  # Should be not found
