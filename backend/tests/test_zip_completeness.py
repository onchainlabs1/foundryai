"""
T2: ZIP Completeness Check
Ensure all required artifacts present in export.
"""

import os
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


def test_annex_iv_zip_completeness(setup_test_data):
    """Test that Annex IV ZIP contains all required documents."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for ZIP completeness",
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
    assert response.headers["content-type"] == "application/zip"
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        # Extract and list files
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # Required core documents
            required_documents = [
                "manifest.json",  # Always required
            ]
            
            # Check for required documents
            for doc in required_documents:
                assert doc in file_list, f"Missing required document: {doc}"
            
            # Expected document patterns (at least one of each type should exist)
            document_patterns = {
                "markdown": [f for f in file_list if f.endswith('.md')],
                "csv": [f for f in file_list if f.endswith('.csv')],
                "json": [f for f in file_list if f.endswith('.json')],
            }
            
            # Should have at least one markdown document
            assert len(document_patterns["markdown"]) > 0, "No markdown documents found"
            
            # Should have at least one JSON document (manifest)
            assert len(document_patterns["json"]) > 0, "No JSON documents found"
            
            # Check for common Annex IV documents (if they exist, they should be valid)
            common_docs = [
                "annex_iv.md",
                "fria.md",
                "soa.csv",
                "monitoring_report.md",
                "controls.csv",
                "risk_register.md",
                "evidence_manifest.csv"
            ]
            
            # Log which common documents are present
            present_docs = [doc for doc in common_docs if doc in file_list]
            print(f"Present documents: {present_docs}")
            
            # Check for unexpected file types (warn but don't fail)
            unexpected_extensions = set()
            for filename in file_list:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.md', '.csv', '.json', '.txt', '.pdf']:
                    unexpected_extensions.add(ext)
            
            if unexpected_extensions:
                print(f"Warning: Unexpected file extensions found: {unexpected_extensions}")
            
            # Verify no empty files
            for filename in file_list:
                file_info = zip_file.getinfo(filename)
                assert file_info.file_size > 0, f"Empty file found: {filename}"
            
            # Verify no duplicate filenames (case-insensitive)
            lowercase_names = [name.lower() for name in file_list]
            assert len(lowercase_names) == len(set(lowercase_names)), "Duplicate filenames found (case-insensitive)"
            
    finally:
        # Clean up temporary file
        os.unlink(temp_zip_path)


def test_zip_structure_validity(setup_test_data):
    """Test that ZIP structure is valid and files are accessible."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for ZIP structure",
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
        # Test ZIP integrity
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Test that ZIP is not corrupted
            bad_file = zip_file.testzip()
            assert bad_file is None, f"Corrupted file in ZIP: {bad_file}"
            
            # Test that all files can be read
            for filename in zip_file.namelist():
                try:
                    content = zip_file.read(filename)
                    assert isinstance(content, bytes)
                    assert len(content) > 0
                except Exception as e:
                    pytest.fail(f"Cannot read file {filename}: {e}")
            
            # Test that manifest.json is valid JSON
            if "manifest.json" in zip_file.namelist():
                manifest_content = zip_file.read("manifest.json")
                import json
                try:
                    manifest = json.loads(manifest_content.decode('utf-8'))
                    assert isinstance(manifest, dict)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in manifest.json: {e}")
            
    finally:
        os.unlink(temp_zip_path)


def test_zip_filename_sanitization(setup_test_data):
    """Test that filenames in ZIP are properly sanitized."""
    client = setup_test_data["client"]
    
    # Create a test system
    system_data = {
        "name": "Test System",
        "purpose": "Test system for filename sanitization",
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
            for filename in zip_file.namelist():
                # Check for dangerous characters
                dangerous_chars = ['..', '~', '$', '`']
                for char in dangerous_chars:
                    assert char not in filename, f"Dangerous character '{char}' in filename: {filename}"
                
                # Check for absolute paths
                assert not filename.startswith('/'), f"Absolute path in filename: {filename}"
                assert not filename.startswith('\\'), f"Windows absolute path in filename: {filename}"
                
                # Check for reasonable filename length
                assert len(filename) <= 255, f"Filename too long: {filename}"
                
                # Check for valid characters (basic ASCII)
                try:
                    filename.encode('ascii')
                except UnicodeEncodeError:
                    pytest.fail(f"Non-ASCII characters in filename: {filename}")
                
    finally:
        os.unlink(temp_zip_path)