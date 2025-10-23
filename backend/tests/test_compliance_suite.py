"""
Tests for Compliance Suite endpoints.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestComplianceSuite:
    """Test compliance suite endpoints."""
    
    def test_generate_compliance_draft_success(self):
        """Test successful compliance draft generation."""
        payload = {
            "system_id": 1,
            "docs": ["annex_iv", "fria"]
        }
        
        with patch('app.services.compliance_suite.compliance_suite_service') as mock_service:
            mock_service.generate_draft_documents.return_value = {
                "docs": [
                    {
                        "type": "annex_iv",
                        "content": "# Annex IV Test Content",
                        "coverage": 0.75,
                        "sections": [
                            {
                                "key": "section_2_1_architecture",
                                "coverage": 1.0,
                                "paragraphs": [
                                    {
                                        "text": "System architecture description [EV-123 p.1 | sha256:abc123]",
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
                        ],
                        "missing": ["section_8_3_supervision"]
                    }
                ]
            }
            
            response = client.post(
                "/reports/draft",
                json=payload,
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["docs"]) == 1
            assert data["docs"][0]["type"] == "annex_iv"
            assert data["docs"][0]["coverage"] == 0.75
            assert "section_8_3_supervision" in data["docs"][0]["missing"]
    
    def test_generate_compliance_draft_requires_auth(self):
        """Test that compliance draft generation requires authentication."""
        payload = {"system_id": 1, "docs": ["annex_iv"]}
        
        response = client.post("/reports/draft", json=payload)
        
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "API-Key"
    
    def test_generate_compliance_draft_invalid_system(self):
        """Test compliance draft generation with invalid system ID."""
        payload = {"system_id": 999, "docs": ["annex_iv"]}
        
        with patch('app.services.compliance_suite.compliance_suite_service') as mock_service:
            mock_service.generate_draft_documents.side_effect = ValueError("System not found")
            
            response = client.post(
                "/reports/draft",
                json=payload,
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 404
            assert "System not found" in response.json()["detail"]
    
    def test_export_document_md(self):
        """Test exporting document in Markdown format."""
        with patch('app.services.compliance_suite.compliance_suite_service') as mock_service:
            mock_service.export_document.return_value = (
                "annex_iv-1-20231215120000.md",
                b"# Annex IV Test Content"
            )
            
            response = client.get(
                "/reports/export/annex_iv.md?system_id=1",
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/markdown"
            assert "attachment" in response.headers["content-disposition"]
            assert "annex_iv-1-20231215120000.md" in response.headers["content-disposition"]
    
    def test_export_document_docx(self):
        """Test exporting document in DOCX format."""
        with patch('app.services.compliance_suite.compliance_suite_service') as mock_service:
            mock_service.export_document.return_value = (
                "fria-1-20231215120000.docx",
                b"DOCX_CONTENT_BYTES"
            )
            
            response = client.get(
                "/reports/export/fria.docx?system_id=1",
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
            assert "fria-1-20231215120000.docx" in response.headers["content-disposition"]
    
    def test_export_document_pdf_disabled(self):
        """Test PDF export when disabled."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.ENABLE_PDF_EXPORT = False
            
            response = client.get(
                "/reports/export/annex_iv.pdf?system_id=1",
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 424
            assert "PDF export is disabled" in response.json()["detail"]
    
    def test_export_document_invalid_type(self):
        """Test export with invalid document type."""
        response = client.get(
            "/reports/export/invalid_type.md?system_id=1",
            headers={"X-API-Key": "dev-aims-demo-key"}
        )
        
        assert response.status_code == 400
        assert "Invalid document type" in response.json()["detail"]
    
    def test_export_document_invalid_format(self):
        """Test export with invalid format."""
        response = client.get(
            "/reports/export/annex_iv.invalid?system_id=1",
            headers={"X-API-Key": "dev-aims-demo-key"}
        )
        
        assert response.status_code == 400
        assert "Invalid format" in response.json()["detail"]
    
    def test_export_document_requires_auth(self):
        """Test that document export requires authentication."""
        response = client.get("/reports/export/annex_iv.md?system_id=1")
        
        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "API-Key"
    
    def test_view_evidence_page_success(self):
        """Test successful evidence page viewing."""
        with patch('app.services.s3.s3_service') as mock_s3:
            mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned-url"
            
            with patch('app.core.config.settings') as mock_settings:
                mock_settings.use_s3 = True
                mock_settings.S3_URL_EXP_MIN = 15
                
                response = client.get(
                    "/reports/evidence/view?evidence_id=123&page=5",
                    headers={"X-API-Key": "dev-aims-demo-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["evidence_id"] == 123
                assert data["page"] == 5
                assert "viewer_url" in data
                assert "page=5" in data["viewer_url"]
    
    def test_view_evidence_page_not_found(self):
        """Test evidence page viewing with non-existent evidence."""
        response = client.get(
            "/reports/evidence/view?evidence_id=999&page=1",
            headers={"X-API-Key": "dev-aims-demo-key"}
        )
        
        assert response.status_code == 404
        assert "Evidence not found" in response.json()["detail"]
    
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
    
    def test_refine_document_enabled(self):
        """Test LLM refinement when feature is enabled."""
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
            mock_settings.FEATURE_LLM_REFINE = True
            
            response = client.post(
                "/reports/refine",
                json=payload,
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["paragraphs"]) == 1
            assert "refined_at" in data
    
    def test_export_soa_narrative(self):
        """Test exporting SoA narrative."""
        with patch('app.services.compliance_suite.compliance_suite_service') as mock_service:
            mock_service.export_document.return_value = (
                "soa-1-20231215120000.md",
                b"# SoA Test Content"
            )
            
            response = client.get(
                "/export/soa.md?system_id=1",
                headers={"X-API-Key": "dev-aims-demo-key"}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/markdown"
            assert "soa-1-20231215120000.md" in response.headers["content-disposition"]


class TestCitationEnforcement:
    """Test citation enforcement in generated content."""
    
    def test_paragraph_has_citation(self):
        """Test that generated paragraphs include citations."""
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
        
        assert "[EV-123 p.5 | sha256:abc123def456]" in paragraph["text"]
        assert len(paragraph["citations"]) == 1
        assert paragraph["citations"][0]["evidence_id"] == 123
        assert paragraph["citations"][0]["page"] == 5
    
    def test_missing_evidence_returns_missing_placeholder(self):
        """Test that missing evidence returns appropriate placeholder."""
        from app.services.compliance_suite import ComplianceSuiteService
        
        service = ComplianceSuiteService()
        
        paragraph = service._generate_evidence_paragraph(
            [], "section_2_1_architecture"
        )
        
        assert "[MISSING] Provide evidence for section_2_1_architecture" in paragraph["text"]
        assert len(paragraph["citations"]) == 0
