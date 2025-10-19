"""
Document Generation Service for AIMS Readiness
Generates ISO/IEC 42001 and EU AI Act compliance documents from onboarding data.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import markdown

# Try to import WeasyPrint, but make it optional
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"Warning: WeasyPrint not available ({e}). PDF generation will be disabled.")

# For testing fallback behavior, uncomment the line below:
# WEASYPRINT_AVAILABLE = False

from app.database import get_db
from app.models import AISystem, Organization, Evidence
from sqlalchemy.orm import Session

# Set up logger
logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generates compliance documents from system and onboarding data."""
    
    def __init__(self):
        # Go up from backend/app/services/ to project root
        self.templates_dir = Path(__file__).parent.parent.parent.parent / "aims_readiness_templates_en"
        self.output_dir = Path(__file__).parent.parent.parent / "generated_documents"
        self.output_dir.mkdir(exist_ok=True)
        
        # Debug: log the actual path being used
        logger.debug(f"Templates directory: {self.templates_dir}")
        logger.debug(f"Templates directory exists: {self.templates_dir.exists()}")
        if self.templates_dir.exists():
            logger.debug(f"Templates found: {list(self.templates_dir.glob('*.md'))}")
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Font configuration for PDF generation (only if WeasyPrint is available)
        if WEASYPRINT_AVAILABLE:
            self.font_config = FontConfiguration()
        else:
            self.font_config = None
    
    def generate_all_documents(self, system_id: int, org_id: int, onboarding_data: Dict[str, Any], db: Session = None) -> Dict[str, str]:
        """
        Generate all compliance documents for a system.
        
        Returns:
            Dict mapping document types to file paths
        """
        if db is None:
            db = next(get_db())
            should_close = True
        else:
            should_close = False
            
        try:
            system = db.query(AISystem).filter(
                AISystem.id == system_id,
                AISystem.org_id == org_id
            ).first()
            
            if not system:
                raise ValueError(f"System {system_id} not found for organization {org_id}")
            
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise ValueError(f"Organization {org_id} not found")
            
            # Create system-specific output directory
            system_dir = self.output_dir / f"org_{org_id}" / f"system_{system_id}"
            system_dir.mkdir(parents=True, exist_ok=True)
            
            generated_docs = {}
            
            # Document generation mapping
            document_templates = {
                "risk_assessment": "01_RISK_ASSESSMENT.md",
                "impact_assessment": "02_IMPACT_ASSESSMENT.md", 
                "model_card": "03_MODEL_CARD.md",
                "data_sheet": "04_DATA_SHEET.md",
                "logging_plan": "05_LOGGING_PLAN.md",
                "monitoring_report": "06_PM_MONITORING_REPORT.md",
                "human_oversight": "07_HUMAN_OVERSIGHT_SOP.md",
                "appeals_flow": "08_APPEALS_FLOW.md",
                "soa": "09_SOA_TEMPLATE.md",
                "policy_register": "10_POLICY_REGISTER.md",
                "audit_log": "11_AUDIT_LOG.md"
            }
            
            # Generate each document
            for doc_type, template_file in document_templates.items():
                try:
                    # Generate Markdown
                    md_path = system_dir / f"{doc_type}.md"
                    md_content = self._generate_document(
                        template_file, 
                        system, 
                        org, 
                        onboarding_data
                    )
                    
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    
                    # Generate PDF (only if WeasyPrint is available)
                    if WEASYPRINT_AVAILABLE:
                        pdf_path = system_dir / f"{doc_type}.pdf"
                        self._generate_pdf(md_content, pdf_path)
                        generated_docs[doc_type] = {
                            "markdown_available": True,
                            "pdf_available": True
                        }
                    else:
                        generated_docs[doc_type] = {
                            "markdown_available": True,
                            "pdf_available": False
                        }
                    
                except Exception as e:
                    logger.error(f"Error generating {doc_type}: {e}")
                    continue
            
            return generated_docs
            
        finally:
            if should_close:
                db.close()
    
    def _generate_document(self, template_file: str, system: AISystem, org: Organization, 
                          onboarding_data: Dict[str, Any]) -> str:
        """Generate a single document from template and data."""
        
        template = self.jinja_env.get_template(template_file)
        
        # Prepare template context
        context = {
            "system": system,
            "organization": org,
            "onboarding": onboarding_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }
        
        # Add computed fields
        context.update(self._compute_document_fields(system, org, onboarding_data))
        
        return template.render(**context)
    
    def _compute_document_fields(self, system: AISystem, org: Organization, 
                                onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute additional fields for document templates."""
        
        # Extract data from onboarding
        company_data = onboarding_data.get("company", {})
        risks_data = onboarding_data.get("risks", {})
        oversight_data = onboarding_data.get("oversight", {})
        monitoring_data = onboarding_data.get("monitoring", {})
        
        return {
            "company_name": company_data.get("name", org.name),
            "company_address": company_data.get("address", ""),
            "company_industry": company_data.get("industry", ""),
            "system_purpose": system.purpose or "AI System",
            "system_domain": system.domain or "General",
            "ai_act_classification": system.ai_act_class or "minimal",
            "is_gpai": system.is_general_purpose_ai,
            "uses_biometrics": system.uses_biometrics,
            "impacts_rights": system.impacts_fundamental_rights,
            "personal_data": system.personal_data_processed,
            "top_risks": risks_data.get("topRisks", []),
            "risk_mitigation": risks_data.get("mitigationStrategies", []),
            "human_oversight_rules": oversight_data.get("oversightRules", []),
            "escalation_paths": oversight_data.get("escalationPaths", []),
            "monitoring_metrics": monitoring_data.get("keyMetrics", []),
            "review_frequency": monitoring_data.get("reviewFrequency", "Quarterly")
        }
    
    def _generate_pdf(self, markdown_content: str, output_path: Path):
        """Convert Markdown to PDF using WeasyPrint."""
        
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint is not available. Cannot generate PDF.")
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Wrap in HTML structure with CSS
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Compliance Document</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #7f8c8d;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html_content}
            <div class="footer">
                <p>Generated by AIMS Readiness Platform on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=full_html).write_pdf(
            str(output_path),
            font_config=self.font_config
        )
    
    def get_document_list(self, system_id: int, org_id: int) -> List[Dict[str, Any]]:
        """Get list of generated documents for a system."""
        
        system_dir = self.output_dir / f"org_{org_id}" / f"system_{system_id}"
        
        if not system_dir.exists():
            return []
        
        documents = []
        document_types = {
            "risk_assessment": "Risk Assessment",
            "impact_assessment": "Impact Assessment", 
            "model_card": "Model Card",
            "data_sheet": "Data Sheet",
            "logging_plan": "Logging Plan",
            "monitoring_report": "Monitoring Report",
            "human_oversight": "Human Oversight SOP",
            "appeals_flow": "Appeals Flow",
            "soa": "Statement of Applicability",
            "policy_register": "Policy Register",
            "audit_log": "Audit Log"
        }
        
        for doc_type, doc_name in document_types.items():
            md_path = system_dir / f"{doc_type}.md"
            pdf_path = system_dir / f"{doc_type}.pdf"
            
            if md_path.exists():
                # Get file stats
                md_stat = md_path.stat()
                
                doc_info = {
                    "type": doc_type,
                    "name": doc_name,
                    "markdown_available": True,
                    "markdown_size": md_stat.st_size,
                    "created_at": datetime.fromtimestamp(md_stat.st_ctime, tz=timezone.utc).isoformat(),
                    "updated_at": datetime.fromtimestamp(md_stat.st_mtime, tz=timezone.utc).isoformat()
                }
                
                # Add PDF info if available
                if pdf_path.exists():
                    pdf_stat = pdf_path.stat()
                    doc_info.update({
                        "pdf_available": True,
                        "pdf_size": pdf_stat.st_size
                    })
                else:
                    doc_info["pdf_available"] = False
                    doc_info["pdf_size"] = None
                
                documents.append(doc_info)
        
        return sorted(documents, key=lambda x: x["name"])
    
    def get_document_content(self, system_id: int, org_id: int, doc_type: str, format: str = "markdown") -> bytes:
        """Get document content for download."""
        
        system_dir = self.output_dir / f"org_{org_id}" / f"system_{system_id}"
        
        if format == "markdown":
            file_path = system_dir / f"{doc_type}.md"
        elif format == "pdf":
            if not WEASYPRINT_AVAILABLE:
                # Fallback to markdown if PDF is not available
                file_path = system_dir / f"{doc_type}.md"
                format = "markdown"  # Override format for consistent response
            else:
                file_path = system_dir / f"{doc_type}.pdf"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document {doc_type} not found for system {system_id}")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Return content with format info for the endpoint to handle
        return content, format
