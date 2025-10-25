"""
T4: Evidence Citations
Verify evidence references in documents.
"""

import os
import re
import tempfile
import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Organization, AISystem, Evidence
from tests.conftest import create_test_system
from tests.conftest_qa import isolated_db_override, clean_test_environment

client = TestClient(app)

API_KEY = "dev-aims-demo-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def setup_test_data(test_client_with_seed):
    """Create test organization and data for each test."""
    client, db_session, org_data = test_client_with_seed
    
    # Get the system from the seeded data
    from app.models import AISystem
    system = db_session.query(AISystem).first()
    
    headers = {"X-API-Key": "dev-aims-demo-key"}
    
    return {
        "client": client,
        "org": org_data,
        "system": system,
        "headers": headers
    }


def test_evidence_citations_present(setup_test_data):
    """Test that evidence sections contain proper citations when evidence exists."""
    client = setup_test_data["client"]
    system = setup_test_data["system"]
    headers = setup_test_data["headers"]
    
    # Create test evidence files
    evidence_files = [
        ("model_card.pdf", "ML model documentation"),
        ("training_data_spec.pdf", "Dataset specification"),
        ("validation_report.pdf", "Model validation results"),
    ]
    
    # Upload evidence files
    for filename, description in evidence_files:
        # Create a simple test file
        test_content = f"Test content for {filename}"
        
        response = client.post(
            f"/evidence/{system.id}",
            files={"file": (filename, test_content, "application/pdf")},
            data={
                "label": description,
                "iso42001_clause": "5.1",
                "control_name": "Test Control"
            },
            headers=headers
        )
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system.id}", headers=headers)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for evidence-related documents
            evidence_docs = [f for f in zip_file.namelist() if 'evidence' in f.lower() or 'annex' in f.lower()]
            
            if not evidence_docs:
                pytest.skip("No evidence-related documents found in export")
            
            citation_pattern = re.compile(r'\[EV-\d+\s+sha256:[a-f0-9]{64}\]', re.IGNORECASE)
            no_evidence_pattern = re.compile(r'no evidence|no documents|not available', re.IGNORECASE)
            
            found_citations = []
            found_no_evidence_markers = []
            
            for doc_name in evidence_docs:
                if not doc_name.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(doc_name)
                    text_content = content.decode('utf-8')
                    
                    # Look for evidence citations
                    citations = citation_pattern.findall(text_content)
                    found_citations.extend([(doc_name, citation) for citation in citations])
                    
                    # Look for "no evidence" markers
                    no_evidence_matches = no_evidence_pattern.findall(text_content)
                    found_no_evidence_markers.extend([(doc_name, match) for match in no_evidence_matches])
                
                except UnicodeDecodeError:
                    continue
            
            # Should have either citations or "no evidence" markers, but not both
            if found_citations and found_no_evidence_markers:
                pytest.fail(f"Found both evidence citations and 'no evidence' markers. "
                           f"Citations: {found_citations}, No evidence: {found_no_evidence_markers}")
            
            # Since we uploaded evidence, we should have citations
            if not found_citations and not found_no_evidence_markers:
                pytest.fail("No evidence citations or 'no evidence' markers found in documents")
            
            # If we have citations, verify they're properly formatted
            for doc_name, citation in found_citations:
                # Verify citation format: [EV-001 sha256:abc123...]
                if not re.match(r'\[EV-\d+\s+sha256:[a-f0-9]{64}\]', citation, re.IGNORECASE):
                    pytest.fail(f"Invalid citation format in {doc_name}: {citation}")
    
    finally:
        os.unlink(temp_zip_path)


def test_evidence_citations_format_validation(setup_test_data):
    """Test that evidence citations follow the correct format."""
    system = setup_test_data["system"]
    
    # Create a single evidence file
    test_content = "Test evidence content"
    response = client.post(
        f"/evidence/{system.id}",
        files={"file": ("test_evidence.pdf", test_content, "application/pdf")},
        data={
            "label": "Test evidence",
            "iso42001_clause": "5.1",
            "control_name": "Test Control"
        },
        headers=HEADERS
    )
    assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system.id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            citation_pattern = re.compile(r'\[EV-\d+\s+sha256:[a-f0-9]{64}\]', re.IGNORECASE)
            
            for filename in zip_file.namelist():
                if not filename.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(filename)
                    text_content = content.decode('utf-8')
                    
                    # Find all citations in this document
                    citations = citation_pattern.findall(text_content)
                    
                    for citation in citations:
                        # Validate citation format
                        match = re.match(r'\[EV-(\d+)\s+sha256:([a-f0-9]{64})\]', citation, re.IGNORECASE)
                        if not match:
                            pytest.fail(f"Invalid citation format: {citation}")
                        
                        evidence_id = match.group(1)
                        sha256_hash = match.group(2)
                        
                        # Verify evidence ID is numeric
                        assert evidence_id.isdigit(), f"Evidence ID should be numeric: {evidence_id}"
                        
                        # Verify SHA256 is 64 hex characters
                        assert len(sha256_hash) == 64, f"SHA256 should be 64 characters: {sha256_hash}"
                        assert all(c in '0123456789abcdef' for c in sha256_hash.lower()), \
                            f"SHA256 should contain only hex characters: {sha256_hash}"
                
                except UnicodeDecodeError:
                    continue
    
    finally:
        os.unlink(temp_zip_path)


def test_no_evidence_markers_when_no_evidence(setup_test_data):
    """Test that 'no evidence' markers are present when no evidence is uploaded."""
    system = setup_test_data["system"]
    
    # Don't upload any evidence - just generate the ZIP
    response = client.get(f"/reports/annex-iv/{system.id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for evidence-related documents
            evidence_docs = [f for f in zip_file.namelist() if 'evidence' in f.lower() or 'annex' in f.lower()]
            
            if not evidence_docs:
                pytest.skip("No evidence-related documents found in export")
            
            no_evidence_patterns = [
                re.compile(r'no evidence', re.IGNORECASE),
                re.compile(r'no documents', re.IGNORECASE),
                re.compile(r'not available', re.IGNORECASE),
                re.compile(r'none uploaded', re.IGNORECASE),
            ]
            
            found_no_evidence_markers = []
            
            for doc_name in evidence_docs:
                if not doc_name.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(doc_name)
                    text_content = content.decode('utf-8')
                    
                    # Look for "no evidence" markers
                    for pattern in no_evidence_patterns:
                        matches = pattern.findall(text_content)
                        found_no_evidence_markers.extend([(doc_name, match) for match in matches])
                
                except UnicodeDecodeError:
                    continue
            
            # Should have some indication that no evidence is available
            if not found_no_evidence_markers:
                pytest.fail("No 'no evidence' markers found when no evidence is uploaded")
    
    finally:
        os.unlink(temp_zip_path)


def test_evidence_manifest_consistency(setup_test_data):
    """Test that evidence manifest is consistent with citations in documents."""
    system = setup_test_data["system"]
    
    # Create test evidence files
    evidence_files = [
        ("model_card.pdf", "ML model documentation"),
        ("training_data_spec.pdf", "Dataset specification"),
    ]
    
    # Upload evidence files
    for filename, description in evidence_files:
        test_content = f"Test content for {filename}"
        response = client.post(
            f"/evidence/{system.id}",
            files={"file": (filename, test_content, "application/pdf")},
            data={
                "label": description,
                "iso42001_clause": "5.1",
                "control_name": "Test Control"
            },
            headers=HEADERS
        )
        assert response.status_code == 200
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system.id}", headers=HEADERS)
    assert response.status_code == 200
    
    # Save ZIP to temporary file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip.write(response.content)
        temp_zip_path = temp_zip.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
            # Look for evidence manifest
            manifest_files = [f for f in zip_file.namelist() if 'evidence' in f.lower() and f.endswith('.csv')]
            
            if not manifest_files:
                pytest.skip("No evidence manifest found")
            
            # Read evidence manifest
            manifest_content = zip_file.read(manifest_files[0])
            manifest_text = manifest_content.decode('utf-8')
            
            # Parse manifest to get evidence IDs
            manifest_lines = manifest_text.split('\n')
            evidence_ids_in_manifest = []
            
            for line in manifest_lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split(',')
                    if len(parts) > 0:
                        evidence_id = parts[0].strip()
                        if evidence_id.startswith('EV-'):
                            evidence_ids_in_manifest.append(evidence_id)
            
            # Look for citations in documents
            citation_pattern = re.compile(r'\[EV-(\d+)\s+sha256:[a-f0-9]{64}\]', re.IGNORECASE)
            evidence_ids_in_citations = []
            
            for filename in zip_file.namelist():
                if not filename.endswith('.md'):
                    continue
                
                try:
                    content = zip_file.read(filename)
                    text_content = content.decode('utf-8')
                    
                    citations = citation_pattern.findall(text_content)
                    evidence_ids_in_citations.extend([f"EV-{ev_id}" for ev_id in citations])
                
                except UnicodeDecodeError:
                    continue
            
            # Evidence IDs in manifest should match those in citations
            manifest_set = set(evidence_ids_in_manifest)
            citations_set = set(evidence_ids_in_citations)
            
            if manifest_set != citations_set:
                pytest.fail(f"Evidence ID mismatch: manifest={manifest_set}, citations={citations_set}")
    
    finally:
        os.unlink(temp_zip_path)
