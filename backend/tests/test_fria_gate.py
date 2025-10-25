"""
T6: FRIA Gate Enforcement
Verify FRIA requirement blocking.
"""

import os
import tempfile
import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Organization, AISystem
from tests.conftest import create_test_system
from tests.conftest_qa import with_isolated_client


@pytest.fixture
def setup_test_data(with_isolated_client):
    """Create test organization and data for each test."""
    client, db_session = with_isolated_client
    
    # Create test organization
    org = Organization(
        name="Test Organization",
        api_key="dev-aims-demo-key"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    headers = {"X-API-Key": "dev-aims-demo-key"}
    
    return {
        "client": client,
        "db_session": db_session,
        "org": org,
        "headers": headers
    }


def test_fria_required_blocks_export(setup_test_data):
    """Test that high-risk systems without FRIA cannot export Annex IV."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    
    # Create high-risk system that requires FRIA
    system_data = {
        "name": "High-Risk AI System",
        "purpose": "Automated decision making",
        "domain": "finance",
        "ai_act_class": "high",
        "impacts_fundamental_rights": True  # This will trigger requires_fria=True
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Attempt to export Annex IV without submitting FRIA
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    
    # Should be blocked (409 Conflict or similar)
    assert response.status_code in [409, 400, 422], f"Expected blocking response, got {response.status_code}"
    
    # Response should indicate FRIA is required
    if response.status_code == 409:
        response_data = response.json()
        assert "fria" in response_data.get("detail", "").lower() or "required" in response_data.get("detail", "").lower()


def test_fria_submitted_allows_export(setup_test_data):
    """Test that high-risk systems with submitted FRIA can export Annex IV."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    org = setup_test_data["org"]
    
    # Create high-risk system
    system_data = {
        "name": "High-Risk AI System with FRIA",
        "purpose": "Automated decision making",
        "domain": "finance",
        "ai_act_class": "high",
        "impacts_fundamental_rights": True
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Submit FRIA
    fria_data = {
        "system_id": system_id,
        "applicable": True,
        "answers": {
            "biometric_data": "No",
            "fundamental_rights": "Yes",
            "critical_infrastructure": "No",
            "vulnerable_groups": "Yes",
            "high_risk_area": "Yes"
        }
    }
    response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers=headers)
    assert response.status_code == 200
    
    # Now attempt to export Annex IV
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    
    # Verify FRIA document is in the ZIP
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Should contain FRIA document
            fria_files = [f for f in zip_file.namelist() if 'fria' in f.lower()]
            assert len(fria_files) > 0, "FRIA document not found in export"
            
            # Check manifest includes FRIA
            if "manifest.json" in zip_file.namelist():
                import json
                manifest_content = zip_file.read("manifest.json")
                manifest = json.loads(manifest_content.decode('utf-8'))
                
                # FRIA should be listed in artifacts
                artifact_filenames = [a["name"] for a in manifest.get("artifacts", [])]
                fria_in_manifest = any('fria' in f.lower() for f in artifact_filenames)
                assert fria_in_manifest, "FRIA not listed in manifest artifacts"
    
    finally:
        os.unlink(temp_zip_path)


def test_low_risk_system_no_fria_required(setup_test_data):
    """Test that low-risk systems don't require FRIA for export."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    org = setup_test_data["org"]
    
    # Create low-risk system
    system_data = {
        "name": "Low-Risk AI System",
        "purpose": "Simple automation",
        "domain": "productivity",
        "ai_act_class": "minimal",
        "requires_fria": False
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Should be able to export without FRIA
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"


def test_fria_gate_error_messages(setup_test_data):
    """Test that FRIA gate provides clear error messages."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    org = setup_test_data["org"]
    
    # Create high-risk system
    system_data = {
        "name": "High-Risk System for Error Testing",
        "purpose": "Critical decision making",
        "domain": "healthcare",
        "ai_act_class": "high",
        "impacts_fundamental_rights": True
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Attempt export and check error message
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    
    if response.status_code in [409, 400, 422]:
        response_data = response.json()
        error_detail = response_data.get("detail", "").lower()
        
        # Error message should mention FRIA or requirement
        fria_mentioned = "fria" in error_detail
        requirement_mentioned = any(word in error_detail for word in ["required", "missing", "complete"])
        
        assert fria_mentioned or requirement_mentioned, \
            f"Error message should mention FRIA or requirement: {response_data}"


def test_fria_status_affects_export(setup_test_data):
    """Test that FRIA status (applicable/not applicable) affects export behavior."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    org = setup_test_data["org"]
    
    # Create high-risk system
    system_data = {
        "name": "High-Risk System for Status Testing",
        "purpose": "Automated assessment",
        "domain": "education",
        "ai_act_class": "high",
        "impacts_fundamental_rights": True
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Submit FRIA as not applicable
    fria_data = {
        "system_id": system_id,
        "applicable": False,
        "answers": {
            "biometric_data": "No",
            "fundamental_rights": "No",
            "critical_infrastructure": "No",
            "vulnerable_groups": "No",
            "high_risk_area": "No"
        }
    }
    response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers=headers)
    assert response.status_code == 200
    
    # Should be able to export with FRIA marked as not applicable (but still submitted)
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify FRIA document reflects not applicable status
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            fria_files = [f for f in zip_file.namelist() if 'fria' in f.lower() and f.endswith('.md')]
            
            if fria_files:
                fria_content = zip_file.read(fria_files[0])
                fria_text = fria_content.decode('utf-8')
                
                # Should mention that FRIA is not applicable
                assert ("applicable: no" in fria_text.lower() or 
                        "not_applicable" in fria_text.lower() or
                        "not applicable" in fria_text.lower())
    
    finally:
        os.unlink(temp_zip_path)


def test_fria_gate_with_complete_annex_iv(setup_test_data):
    """Test FRIA gate with complete Annex IV export endpoint."""
    client = setup_test_data["client"]
    headers = setup_test_data["headers"]
    org = setup_test_data["org"]
    
    # Create high-risk system
    system_data = {
        "name": "Complete Annex IV Test System",
        "purpose": "Full compliance testing",
        "domain": "finance",
        "ai_act_class": "high",
        "impacts_fundamental_rights": True
    }
    response = client.post("/systems", json=system_data, headers=headers)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test complete Annex IV endpoint without FRIA
    response = client.get(f"/reports/annex-iv-complete/{system_id}", headers=headers)
    
    # Should be blocked
    assert response.status_code in [409, 400, 422], f"Complete Annex IV should be blocked without FRIA, got {response.status_code}"
    
    # Submit FRIA
    fria_data = {
        "system_id": system_id,
        "applicable": True,
        "answers": {
            "biometric_data": "No",
            "fundamental_rights": "Yes",
            "critical_infrastructure": "No",
            "vulnerable_groups": "Yes"
        }
    }
    response = client.post(f"/systems/{system_id}/fria", json=fria_data, headers=headers)
    assert response.status_code == 200
    
    # Now complete Annex IV should work
    response = client.get(f"/reports/annex-iv-complete/{system_id}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
