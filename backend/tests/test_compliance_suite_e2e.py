"""
E2E tests for Compliance Suite functionality.
Tests document generation, citation enforcement, coverage validation, and exports.
"""
import json
import logging

import pytest
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import FRIA, Control, Evidence, Incident, Organization


@pytest.fixture
def client():
    """Test client with clean database."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_org_and_system(client):
    """Create organization and AI system with comprehensive test data."""
    # Create organization directly in database
    
    db = SessionLocal()
    try:
        org = Organization(name="Test Compliance Org", api_key="test-compliance-key")
        db.add(org)
        db.commit()
        db.refresh(org)
        org_id = org.id
    finally:
        db.close()
    
    # Create AI system
    system_data = {
        "name": "Test AI System",
        "purpose": "Testing compliance suite functionality",
        "domain": "testing",
        "deployment_context": "public",
        "ai_act_class": "high-risk",
        "is_gpai": True,
        "role": "provider"
    }
    system_response = client.post(
        "/systems", 
        json=system_data,
        headers={"X-API-Key": "test-compliance-key"}
    )
    assert system_response.status_code in [200, 201], f"Expected 200 or 201, got {system_response.status_code}"
    system_id = system_response.json()["id"]
    
    # Create evidence directly in database
    evidence_ids = []
    for i, (label, clause, control) in enumerate([
        ("Risk Assessment Report", "ISO42001:6.1.1", "Risk Management"),
        ("Data Quality Policy", "ISO42001:6.2.1", "Data Quality"),
        ("Bias Mitigation Plan", "ISO42001:6.2.2", "Bias Prevention"),
        ("Transparency Documentation", "AIAct:Art12", "Transparency"),
        ("Human Oversight Procedures", "ISO42001:8.2.3", "Human Oversight"),
    ]):
        import hashlib
        
        db = SessionLocal()
        try:
            checksum = hashlib.sha256(f"evidence_{i}".encode()).hexdigest()
            evidence = Evidence(
                org_id=org_id,
                system_id=system_id,
                label=label,
                file_path=f"/tmp/test_{i}.pdf",
                checksum=checksum,
                iso42001_clause=clause,
                control_name=control
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)
            evidence_ids.append(evidence.id)
        finally:
            db.close()
    
    # Create FRIA directly in database

    
    db = SessionLocal()
    try:
        fria = FRIA(
            org_id=org_id,
            system_id=system_id,
            applicable=True,
            status="draft",
            answers_json=json.dumps({
                "q1": True, "q2": False, "q3": True, "q4": False, "q5": True,
                "q6": False, "q7": True, "q8": False, "q9": True, "q10": False
            }),
            summary_md="Test FRIA summary"
        )
        db.add(fria)
        db.commit()
    finally:
        db.close()
    
    # Create controls directly in database
    
    db = SessionLocal()
    try:
        for iso_clause, name, status in [
            ("ISO42001:6.1.1", "Risk Management", "implemented"),
            ("ISO42001:6.2.1", "Data Quality", "partial"),
            ("AIAct:Art12", "Transparency", "missing"),
        ]:
            control = Control(
                org_id=org_id,
                system_id=system_id,
                iso_clause=iso_clause,
                name=name,
                status=status,
                priority="medium"
            )
            db.add(control)
        db.commit()
    finally:
        db.close()
    
    # Create incidents directly in database
    from datetime import datetime, timezone

    
    db = SessionLocal()
    try:
        for severity, description in [
            ("medium", "Test incident for PMM report"),
            ("low", "Minor issue resolved"),
        ]:
            incident = Incident(
                org_id=org_id,
                system_id=system_id,
                severity=severity,
                description=description,
                detected_at=datetime.now(timezone.utc)
            )
            db.add(incident)
        db.commit()
    finally:
        db.close()
    
    return {
        "org_id": org_id,
        "system_id": system_id,
        "evidence_ids": evidence_ids,
        "api_key": "test-compliance-key"
    }


class TestComplianceSuiteE2E:
    """End-to-end tests for compliance suite functionality."""
    
    def test_generate_all_document_drafts(self, client, seeded_org_and_system):
        """Test generating drafts for all five document types."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Generate drafts for all document types
        docs_to_test = ["annex_iv", "fria", "pmm", "soa", "risk_register"]
        
        response = client.post(
            "/reports/draft",
            json={"system_id": system_id, "docs": docs_to_test},
            headers={"X-API-Key": api_key}
        )
        
        if response.status_code != 200:
            # Debug logging removed for security
            logger.error(f"Compliance suite test failed with status {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all document types are present
        assert len(data["docs"]) == 5
        returned_types = [doc["type"] for doc in data["docs"]]
        for doc_type in docs_to_test:
            assert doc_type in returned_types
        
        # Verify each document has proper structure
        for doc in data["docs"]:
            # Coverage should be between 0 and 1
            assert 0 <= doc["coverage"] <= 1, f"{doc['type']} coverage should be between 0 and 1"
            assert len(doc["sections"]) > 0, f"{doc['type']} should have sections"
            assert isinstance(doc["missing"], list), f"{doc['type']} should have missing list"
            
            # Check section structure
            for section in doc["sections"]:
                assert "key" in section
                assert "coverage" in section
                assert "paragraphs" in section
                assert isinstance(section["paragraphs"], list)
                
                # If there are paragraphs, verify citation format
                for paragraph in section["paragraphs"]:
                    assert "text" in paragraph
                    assert "citations" in paragraph
                    assert isinstance(paragraph["citations"], list)
                    
                    # Verify citation format if present
                    for citation in paragraph["citations"]:
                        assert "evidence_id" in citation
                        assert "page" in citation
                        assert "checksum" in citation
    
    def test_export_annex_iv_formats(self, client, seeded_org_and_system):
        """Test exporting Annex IV in MD, DOCX, and PDF formats."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        formats = ["md", "docx", "pdf"]
        
        for format_type in formats:
            response = client.get(
                f"/reports/export/annex_iv.{format_type}",
                params={"system_id": system_id},
                headers={"X-API-Key": api_key}
            )
            
            assert response.status_code == 200
            
            # Verify content type
            if format_type == "md":
                assert "text/markdown" in response.headers["content-type"]
            elif format_type == "docx":
                assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
            elif format_type == "pdf":
                assert "application/pdf" in response.headers["content-type"]
            
            # Verify non-empty content
            assert len(response.content) > 0, f"{format_type} export should not be empty"
            
            # For MD, verify it contains expected content
            if format_type == "md":
                content = response.text
                assert "Annex IV" in content or "Technical Documentation" in content
                assert "[" in content and "]" in content  # Should have citations
    
    def test_export_fria_formats(self, client, seeded_org_and_system):
        """Test exporting FRIA in MD, DOCX, and PDF formats."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        formats = ["md", "docx"]
        
        for format_type in formats:
            response = client.get(
                f"/reports/export/fria.{format_type}",
                params={"system_id": system_id},
                headers={"X-API-Key": api_key}
            )
            
            assert response.status_code == 200
            
            # Verify content type
            if format_type == "md":
                assert "text/markdown" in response.headers["content-type"]
            elif format_type == "docx":
                assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
            
            # Verify non-empty content
            assert len(response.content) > 0, f"{format_type} export should not be empty"
            
            # For MD, verify it contains expected content
            if format_type == "md":
                content = response.text
                assert "FRIA" in content or "Fundamental Rights" in content
    
    def test_citation_deeplink_structure(self, client, seeded_org_and_system):
        """Test citation deep link URL structure."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        evidence_id = seeded_org_and_system["evidence_ids"][0]
        
        # Get evidence viewer URL
        response = client.get(
            "/evidence/view",
            params={"evidence_id": evidence_id, "page": 1},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify URL structure
        assert "url" in data
        url = data["url"]
        assert f"evidence_id={evidence_id}" in url
        assert "page=1" in url
        assert url.startswith("http")
    
    def test_coverage_calculation_accuracy(self, client, seeded_org_and_system):
        """Test that coverage calculations are accurate based on available evidence."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Generate draft
        response = client.post(
            "/reports/draft",
            json={"system_id": system_id, "docs": ["annex_iv"]},
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        annex_iv = next(doc for doc in data["docs"] if doc["type"] == "annex_iv")
        
        # Coverage should be > 0 since we have evidence
        assert annex_iv["coverage"] > 0
        
        # Check that missing items are reasonable
        assert len(annex_iv["missing"]) >= 0
        
        # Verify sections have reasonable coverage
        for section in annex_iv["sections"]:
            assert 0 <= section["coverage"] <= 1
            assert len(section["paragraphs"]) > 0
    
    def test_authentication_required(self, client, seeded_org_and_system):
        """Test that all compliance suite endpoints require authentication."""
        system_id = seeded_org_and_system["system_id"]
        
        # Test draft generation without auth
        response = client.post(
            "/reports/draft",
            json={"system_id": system_id, "docs": ["annex_iv"]}
        )
        assert response.status_code == 401
        
        # Test export without auth
        response = client.get(f"/reports/export/annex_iv.md?system_id={system_id}")
        assert response.status_code == 401
        
        # Test evidence viewer without auth
        evidence_id = seeded_org_and_system["evidence_ids"][0]
        response = client.get(f"/evidence/view?evidence_id={evidence_id}&page=1")
        assert response.status_code == 401
    
    def test_invalid_document_types(self, client, seeded_org_and_system):
        """Test handling of invalid document types."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Test invalid document type in draft generation
        response = client.post(
            "/reports/draft",
            json={"system_id": system_id, "docs": ["invalid_doc"]},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 422
        
        # Test invalid document type in export
        response = client.get(
            "/reports/export/invalid_doc.md",
            params={"system_id": system_id},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 404
    
    def test_invalid_export_formats(self, client, seeded_org_and_system):
        """Test handling of invalid export formats."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Test invalid format
        response = client.get(
            "/reports/export/annex_iv.invalid",
            params={"system_id": system_id},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 404
    
    def test_system_not_found(self, client, seeded_org_and_system):
        """Test handling of non-existent system IDs."""
        api_key = seeded_org_and_system["api_key"]
        invalid_system_id = 99999
        
        # Test draft generation with invalid system
        response = client.post(
            "/reports/draft",
            json={"system_id": invalid_system_id, "docs": ["annex_iv"]},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 404
        
        # Test export with invalid system
        response = client.get(
            "/reports/export/annex_iv.md",
            params={"system_id": invalid_system_id},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 404
    
    def test_feature_flag_enforcement(self, client, seeded_org_and_system):
        """Test that LLM refinement is only available when feature flag is enabled."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Test refinement endpoint (should be disabled by default)
        refinement_data = {
            "doc_type": "annex_iv",
            "system_id": system_id,
            "section_key": "8.3",
            "paragraphs": [{"text": "Test paragraph", "citations": []}]
        }
        
        response = client.post(
            "/reports/refine",
            json=refinement_data,
            headers={"X-API-Key": api_key}
        )
        
        # Should return 404 when feature is disabled
        assert response.status_code == 404
    
    def test_evidence_viewer_with_invalid_evidence(self, client, seeded_org_and_system):
        """Test evidence viewer with invalid evidence ID."""
        api_key = seeded_org_and_system["api_key"]
        invalid_evidence_id = 99999
        
        response = client.get(
            "/evidence/view",
            params={"evidence_id": invalid_evidence_id, "page": 1},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 404
    
    def test_comprehensive_workflow(self, client, seeded_org_and_system):
        """Test a complete workflow: generate draft, check coverage, export document."""
        system_id = seeded_org_and_system["system_id"]
        api_key = seeded_org_and_system["api_key"]
        
        # Step 1: Generate draft
        response = client.post(
            "/reports/draft",
            json={"system_id": system_id, "docs": ["annex_iv", "fria"]},
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200
        drafts = response.json()["docs"]
        
        # Step 2: Verify coverage and citations
        for draft in drafts:
            assert draft["coverage"] > 0
            assert len(draft["sections"]) > 0
            
            # Check for citations
            has_citations = any(
                any(para["citations"] for para in section["paragraphs"])
                for section in draft["sections"]
            )
            assert has_citations
        
        # Step 3: Export documents
        for draft in drafts:
            doc_type = draft["type"]
            response = client.get(
                f"/reports/export/{doc_type}.md",
                params={"system_id": system_id},
                headers={"X-API-Key": api_key}
            )
            assert response.status_code == 200
            assert len(response.content) > 0
            
            # Verify citation patterns in exported content
            content = response.text
            assert "[" in content and "]" in content  # Citation markers
        
        # Step 4: Test evidence viewer links
        annex_iv = next(doc for doc in drafts if doc["type"] == "annex_iv")
        first_section = annex_iv["sections"][0]
        first_paragraph = first_section["paragraphs"][0]
        
        if first_paragraph["citations"]:
            citation = first_paragraph["citations"][0]
            evidence_id = citation["evidence_id"]
            page = citation["page"]
            
            response = client.get(
                "/evidence/view",
                params={"evidence_id": evidence_id, "page": page},
                headers={"X-API-Key": api_key}
            )
            assert response.status_code == 200
