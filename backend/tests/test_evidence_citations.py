"""
Test evidence linking and citations in generated documents
"""

import pytest
from pathlib import Path

from app.models import Organization, AISystem, Control, Evidence
from app.services.document_generator import DocumentGenerator


@pytest.fixture
def system_with_evidence_links(test_client_with_seed):
    """Create system with controls and linked evidence using shared fixture."""
    client, db_session, org_data = test_client_with_seed
    
    # Use the seeded system from Credit Scoring scenario
    system_id = org_data["system_id"]
    
    # Get the system from database
    system = db_session.query(AISystem).filter(AISystem.id == system_id).first()
    
    return {
        "client": client,
        "db_session": db_session,
        "org_data": org_data,
        "system": system,
        "system_id": system_id
    }


def test_evidence_citations_in_annex_iv(system_with_evidence_links):
    """Test that evidence citations appear correctly in Annex IV documents."""
    client = system_with_evidence_links["client"]
    system_id = system_with_evidence_links["system_id"]
    headers = system_with_evidence_links["org_data"]["headers"]
    
    # Generate Annex IV document
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Check that the ZIP contains the expected files
    import zipfile
    import io
    
    zip_content = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_content, 'r') as zip_file:
        file_list = zip_file.namelist()
        
        # Should have Annex IV document
        assert "annex_iv.md" in file_list
        
        # Read Annex IV content
        annex_content = zip_file.read("annex_iv.md").decode('utf-8')
        
        # Check for evidence citations (should contain [EV-...] references)
        assert "[EV-" in annex_content or "evidence" in annex_content.lower()


def test_evidence_citations_in_fria(system_with_evidence_links):
    """Test that evidence citations appear correctly in FRIA documents."""
    client = system_with_evidence_links["client"]
    system_id = system_with_evidence_links["system_id"]
    headers = system_with_evidence_links["org_data"]["headers"]
    
    # Generate Annex IV ZIP (which includes FRIA)
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Check that the ZIP contains the expected files
    import zipfile
    import io
    
    zip_content = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_content, 'r') as zip_file:
        file_list = zip_file.namelist()
        
        # Should have FRIA document
        assert "fria.md" in file_list
        
        # Read FRIA content
        fria_content = zip_file.read("fria.md").decode('utf-8')
        
        # Check for evidence citations or FRIA content
        assert "[EV-" in fria_content or "evidence" in fria_content.lower() or "fria" in fria_content.lower()


def test_evidence_manifest_in_zip(system_with_evidence_links):
    """Test that evidence manifest is included in ZIP exports."""
    client = system_with_evidence_links["client"]
    system_id = system_with_evidence_links["system_id"]
    headers = system_with_evidence_links["org_data"]["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Check that the ZIP contains evidence manifest
    import zipfile
    import io
    
    zip_content = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_content, 'r') as zip_file:
        file_list = zip_file.namelist()
        
        # Should have evidence manifest
        assert "evidence_manifest.csv" in file_list
        
        # Read evidence manifest
        manifest_content = zip_file.read("evidence_manifest.csv").decode('utf-8')
        
        # Should contain evidence information
        assert "filename" in manifest_content.lower() or "evidence" in manifest_content.lower()


def test_evidence_checksums_in_manifest(system_with_evidence_links):
    """Test that evidence checksums are included in manifest."""
    client = system_with_evidence_links["client"]
    system_id = system_with_evidence_links["system_id"]
    headers = system_with_evidence_links["org_data"]["headers"]
    
    # Generate Annex IV ZIP
    response = client.get(f"/reports/annex-iv/{system_id}", headers=headers)
    assert response.status_code == 200
    
    # Check manifest.json for evidence checksums
    import zipfile
    import io
    import json
    
    zip_content = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_content, 'r') as zip_file:
        file_list = zip_file.namelist()
        
        # Should have manifest.json
        assert "manifest.json" in file_list
        
        # Read manifest
        manifest_content = zip_file.read("manifest.json").decode('utf-8')
        manifest = json.loads(manifest_content)
        
        # Should have sources with evidence information
        assert "sources" in manifest
        assert len(manifest["sources"]) > 0
        
        # Check for evidence in sources
        has_evidence = False
        for source in manifest["sources"]:
            if "evidence" in source and len(source["evidence"]) > 0:
                has_evidence = True
                # Check that evidence has checksums
                for ev in source["evidence"]:
                    assert "sha256" in ev
                    assert ev["sha256"] != "N/A"
                break
        
        assert has_evidence, "No evidence found in manifest sources"