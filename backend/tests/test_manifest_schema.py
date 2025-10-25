"""
T1: Manifest Schema Validation
Validate ZIP manifest structure and integrity.
"""

import json
import os
import tempfile
import zipfile
from datetime import datetime

import pytest


@pytest.fixture
def setup_test_data(test_client_with_seed):
    """Create test organization and data for each test using shared fixture."""
    client, db_session, org_data = test_client_with_seed
    
    return {
        "client": client,
        "db_session": db_session,
        "org_data": org_data,
        "system_id": org_data["system_id"],
        "headers": org_data["headers"]
    }


def test_manifest_schema_validation(setup_test_data):
    """Test that Annex IV ZIP contains valid manifest.json with required fields."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        # Extract and validate manifest
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Check manifest.json exists
            assert "manifest.json" in zip_file.namelist()
            
            # Read and parse manifest
            manifest_content = zip_file.read("manifest.json")
            manifest = json.loads(manifest_content.decode('utf-8'))
            
            # Validate required fields
            required_fields = [
                "system_id", "generated_at", "generator_version",
                "artifacts", "sources", "approvals"
            ]
            
            for field in required_fields:
                assert field in manifest, f"Missing required field: {field}"
            
            # Validate system_id
            assert manifest["system_id"] == system_id
            
            # Validate generated_at is ISO8601 with timezone
            generated_at = manifest["generated_at"]
            assert isinstance(generated_at, str)
            # Parse to ensure it's valid ISO8601
            parsed_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            assert parsed_time.tzinfo is not None, "generated_at must include timezone"
            
            # Validate generator_version
            assert isinstance(manifest["generator_version"], str)
            assert len(manifest["generator_version"]) > 0
            
            # Validate artifacts is a list
            assert isinstance(manifest["artifacts"], list)
            
            # Validate sources is a list
            assert isinstance(manifest["sources"], list)
            
            # Validate approvals is a list
            assert isinstance(manifest["approvals"], list)
            
            # Validate artifacts have required structure
            for artifact in manifest["artifacts"]:
                assert "name" in artifact
                assert "sha256" in artifact
                assert "bytes" in artifact
                
                # Verify artifact exists in ZIP
                assert artifact["name"] in zip_file.namelist()
                
                # Recompute SHA256 and verify
                file_content = zip_file.read(artifact["name"])
                import hashlib
                computed_sha256 = hashlib.sha256(file_content).hexdigest()
                assert artifact["sha256"] == computed_sha256
                
                # Verify size matches
                assert artifact["bytes"] == len(file_content)
    
    finally:
        # Clean up temporary file
        os.unlink(temp_zip_path)


def test_manifest_integrity_checksum_validation(setup_test_data):
    """Test that all files in ZIP match their declared checksums."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Read manifest
            manifest_content = zip_file.read("manifest.json")
            manifest = json.loads(manifest_content.decode('utf-8'))
            
            # Verify each artifact's checksum
            for artifact in manifest["artifacts"]:
                filename = artifact["name"]
                declared_sha256 = artifact["sha256"]
                
                # Read file content
                file_content = zip_file.read(filename)
                
                # Compute actual checksum
                import hashlib
                actual_sha256 = hashlib.sha256(file_content).hexdigest()
                
                # Verify match
                assert declared_sha256 == actual_sha256, f"Checksum mismatch for {filename}"
    
    finally:
        os.unlink(temp_zip_path)


def test_manifest_contains_expected_artifacts(setup_test_data):
    """Test that manifest includes expected document types."""
    client = setup_test_data["client"]
    system_id = setup_test_data["system_id"]
    headers = setup_test_data["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Read manifest
            manifest_content = zip_file.read("manifest.json")
            manifest = json.loads(manifest_content.decode('utf-8'))
            
            # Check for expected artifacts
            artifact_names = [artifact["name"] for artifact in manifest["artifacts"]]
            
            # Should have manifest.json in the ZIP (but not necessarily in artifacts list)
            assert "manifest.json" in zip_file.namelist()
            
            # Should have some compliance documents
            expected_docs = ["annex_iv.md", "fria.md"]
            found_docs = [doc for doc in expected_docs if doc in artifact_names]
            assert len(found_docs) > 0, f"Expected at least one of {expected_docs}, found {artifact_names}"
            
            # Should have evidence manifest
            assert "evidence_manifest.csv" in artifact_names
            
            # Verify all declared artifacts exist in ZIP
            for artifact in manifest["artifacts"]:
                assert artifact["name"] in zip_file.namelist()
    
    finally:
        os.unlink(temp_zip_path)