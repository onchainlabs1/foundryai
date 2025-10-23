"""
Basic tests for Compliance Suite functionality.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestComplianceSuiteBasic:
    """Basic tests for compliance suite endpoints."""
    
    def test_generate_compliance_draft_requires_auth(self):
        """Test that compliance draft generation requires authentication."""
        payload = {"system_id": 1, "docs": ["annex_iv"]}
        
        response = client.post("/reports/draft", json=payload)
        
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "API-Key"
    
    def test_export_document_requires_auth(self):
        """Test that document export requires authentication."""
        response = client.get("/export/annex_iv.md?system_id=1")
        
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "API-Key"
    
    def test_export_document_invalid_type(self):
        """Test export with invalid document type."""
        response = client.get(
            "/export/invalid_type.md?system_id=1",
            headers={"X-API-Key": "dev-aims-demo-key"}
        )
        
        assert response.status_code == 400
        assert "Invalid document type" in response.json()["detail"]
    
    def test_export_document_invalid_format(self):
        """Test export with invalid format."""
        response = client.get(
            "/export/annex_iv.invalid?system_id=1",
            headers={"X-API-Key": "dev-aims-demo-key"}
        )
        
        assert response.status_code == 400
        assert "Invalid format" in response.json()["detail"]
    
    def test_refine_document_disabled(self):
        """Test LLM refinement when feature is disabled."""
        payload = {
            "doc_type": "annex_iv",
            "system_id": 1,
            "section_key": "section_2_1_architecture",
            "paragraphs": [
                {
                    "text": "Test paragraph [EV-123 p.1 | sha256:abc123]",
                    "citations": [
                        {
                            "evidence_id": 123,
                            "page": 1,
                            "checksum": "abc123"
                        }
                    ]
                }
            ]
        }
        
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.FEATURE_LLM_REFINE = False
            
            response = client.post(
                "/reports/refine",
                json=payload,
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 403
            assert "LLM refinement feature is disabled" in response.json()["detail"]
    
    def test_citation_enforcement_pattern(self):
        """Test that citation patterns are correctly formatted."""
        from app.services.compliance_suite import ComplianceSuiteService
        
        service = ComplianceSuiteService()
        
        # Mock evidence snippets
        evidence_snippets = [
            {
                "evidence_id": 123,
                "page_number": 5,
                "text_content": "System uses machine learning algorithms",
                "checksum": "abc123def456"
            }
        ]
        
        paragraph = service._generate_evidence_paragraph(
            evidence_snippets, "section_2_1_architecture"
        )
        
        # Check citation pattern
        assert "[EV-123 p.5 | sha256:abc123def456]" in paragraph["text"]
        assert len(paragraph["citations"]) == 1
        assert paragraph["citations"][0]["evidence_id"] == 123
        assert paragraph["citations"][0]["page"] == 5
        assert paragraph["citations"][0]["checksum"] == "abc123def456"
    
    def test_missing_evidence_returns_missing_placeholder(self):
        """Test that missing evidence returns appropriate placeholder."""
        from app.services.compliance_suite import ComplianceSuiteService
        
        service = ComplianceSuiteService()
        
        paragraph = service._generate_evidence_paragraph(
            [], "section_2_1_architecture"
        )
        
        assert "[MISSING] Provide evidence for section_2_1_architecture" in paragraph["text"]
        assert len(paragraph["citations"]) == 0
    
    def test_template_loading(self):
        """Test that templates can be loaded."""
        from app.services.compliance_suite import ComplianceSuiteService
        
        service = ComplianceSuiteService()
        
        # Check that templates directory exists
        assert service.templates_dir.exists()
        
        # Check that all required templates exist
        required_templates = [
            "annex_iv.md", "fria.md", "pmm_report.md", 
            "soa.md", "risk_register.md"
        ]
        
        for template_name in required_templates:
            template_path = service.templates_dir / template_name
            assert template_path.exists(), f"Template {template_name} not found"
    
    def test_section_keys_mapping(self):
        """Test that section keys are properly mapped for each document type."""
        from app.services.compliance_suite import ComplianceSuiteService
        
        service = ComplianceSuiteService()
        
        # Test annex_iv section keys
        annex_keys = service._get_section_keys("annex_iv")
        assert len(annex_keys) > 0
        assert "section_2_1_architecture" in annex_keys
        assert "section_8_3_supervision" in annex_keys
        
        # Test fria section keys
        fria_keys = service._get_section_keys("fria")
        assert len(fria_keys) > 0
        assert "section_1_1_system_description" in fria_keys
        assert "section_8_2_recommendations" in fria_keys
        
        # Test invalid document type
        invalid_keys = service._get_section_keys("invalid_doc")
        assert len(invalid_keys) == 0
