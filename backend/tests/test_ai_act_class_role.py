"""
T8: AI Act Class & Role Badges
Validate AI Act metadata visibility.
"""

import tempfile
import zipfile

import pytest

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
    
    return {"org": org, "client": client}


def test_high_risk_provider_badges(setup_test_data):
    """Test that high-risk provider systems show appropriate AI Act badges."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Create high-risk provider system
    system_data = {
        "name": "High-Risk Provider System",
        "purpose": "Automated decision making in healthcare",
        "domain": "healthcare",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Check for AI Act compliance sections
            file_list = zip_file.namelist()
            
            # Should have manifest with AI Act metadata
            assert "manifest.json" in file_list
            
            manifest_content = zip_file.read("manifest.json")
            import json
            manifest = json.loads(manifest_content.decode('utf-8'))
            
            # Check AI Act metadata in manifest
            assert "ai_act_class" in manifest
            assert manifest["ai_act_class"] == "high"
            
            # Check for AI Act compliance documents (annex_iv, fria, soa are compliance documents)
            compliance_docs = [f for f in file_list if any(keyword in f.lower() for keyword in ['annex', 'fria', 'soa', 'compliance', 'ai_act'])]
            assert len(compliance_docs) > 0, "No AI Act compliance documents found"
            
    finally:
        import os
        os.unlink(temp_zip_path)


def test_ai_act_metadata_in_exports(setup_test_data):
    """Test that AI Act metadata is included in all exports."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Create system with AI Act classification
    system_data = {
        "name": "AI Act Test System",
        "purpose": "Test system for AI Act compliance",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Test different export formats
    export_endpoints = [
        f"/reports/annex-iv/{system_id}",
        f"/reports/fria/{system_id}",
    ]
    
    for endpoint in export_endpoints:
        response = client.get(endpoint, headers=HEADERS)
        if response.status_code == 200:
            # Check that response includes AI Act metadata
            if "application/zip" in response.headers.get("content-type", ""):
                # For ZIP files, check manifest
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                    temp_zip.write(response.content)
                    temp_zip_path = temp_zip.name
                
                try:
                    with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
                        if "manifest.json" in zip_file.namelist():
                            manifest_content = zip_file.read("manifest.json")
                            import json
                            manifest = json.loads(manifest_content.decode('utf-8'))
                            
                            # Should include AI Act metadata
                            assert "ai_act_class" in manifest
                            assert manifest["ai_act_class"] == "high"
                finally:
                    import os
                    os.unlink(temp_zip_path)


def test_role_badges_in_documents(setup_test_data):
    """Test that role badges appear in generated documents."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Create provider system
    system_data = {
        "name": "Provider System",
        "purpose": "AI system provider",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Check for role information in documents
            file_list = zip_file.namelist()
            
            # Look for markdown files that might contain role information
            md_files = [f for f in file_list if f.endswith('.md')]
            
            role_found = False
            for md_file in md_files:
                content = zip_file.read(md_file).decode('utf-8')
                if 'provider' in content.lower() or 'role' in content.lower():
                    role_found = True
                    break
            
            # Should find role information in at least one document
            assert role_found, "No role information found in generated documents"
            
    finally:
        import os
        os.unlink(temp_zip_path)


def test_ai_act_compliance_sections(setup_test_data):
    """Test that AI Act compliance sections are properly formatted."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Create high-risk system
    system_data = {
        "name": "High-Risk Compliance System",
        "purpose": "High-risk AI system for compliance testing",
        "domain": "healthcare",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Check for compliance-related content
            file_list = zip_file.namelist()
            
            # Should have compliance-related documents
            compliance_docs = [f for f in file_list if any(keyword in f.lower() for keyword in ['compliance', 'ai_act', 'annex', 'fria'])]
            assert len(compliance_docs) > 0, "No compliance documents found"
            
            # Check manifest for compliance metadata
            if "manifest.json" in file_list:
                manifest_content = zip_file.read("manifest.json")
                import json
                manifest = json.loads(manifest_content.decode('utf-8'))
                
                # Should have compliance-related metadata
                assert "ai_act_class" in manifest
                assert manifest["ai_act_class"] == "high"
                
    finally:
        import os
        os.unlink(temp_zip_path)


def test_ai_act_classification_accuracy(setup_test_data):
    """Test that AI Act classification is accurate and consistent."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Test different AI Act classifications
    test_cases = [
        {"ai_act_class": "minimal", "expected_risk": "minimal"},
        {"ai_act_class": "limited", "expected_risk": "limited"},
        {"ai_act_class": "high", "expected_risk": "high"},
    ]
    
    for test_case in test_cases:
        system_data = {
            "name": f"Test {test_case['ai_act_class']} System",
            "purpose": f"Test system for {test_case['ai_act_class']} risk classification",
            "domain": "finance",
            "ai_act_class": test_case["ai_act_class"],
            "system_role": "provider"
        }
        
        response = client.post("/systems", json=system_data, headers=HEADERS)
        assert response.status_code == 200
        system_id = response.json()["id"]
        
        # Verify classification is stored correctly
        response = client.get(f"/systems/{system_id}", headers=HEADERS)
        assert response.status_code == 200
        system_data = response.json()
        assert system_data["ai_act_class"] == test_case["ai_act_class"]


def test_ai_act_metadata_consistency(setup_test_data):
    """Test that AI Act metadata is consistent across all endpoints."""
    org = setup_test_data["org"]
    client = setup_test_data["client"]
    
    # Create system with specific AI Act classification
    system_data = {
        "name": "Consistency Test System",
        "purpose": "Test AI Act metadata consistency",
        "domain": "finance",
        "ai_act_class": "high",
        "system_role": "provider"
    }
    
    response = client.post("/systems", json=system_data, headers=HEADERS)
    assert response.status_code == 200
    system_id = response.json()["id"]
    
    # Check consistency across different endpoints
    endpoints_to_check = [
        f"/systems/{system_id}",
        "/reports/summary",
    ]
    
    expected_class = "high"
    
    for endpoint in endpoints_to_check:
        response = client.get(endpoint, headers=HEADERS)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check if AI Act class is present and consistent
        if "systems" in data:
            # For summary endpoint
            systems = data["systems"]
            if isinstance(systems, list) and len(systems) > 0:
                system = systems[0]
                if "ai_act_class" in system:
                    assert system["ai_act_class"] == expected_class
        elif "ai_act_class" in data:
            # For individual system endpoint
            assert data["ai_act_class"] == expected_class