"""
Document generation and management endpoints.
"""

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, Organization
from app.services.document_generator import DocumentGenerator

router = APIRouter(prefix="/documents", tags=["documents"])

# Valid document types whitelist
VALID_DOCUMENT_TYPES = {
    "risk_assessment",
    "impact_assessment", 
    "model_card",
    "data_sheet",
    "logging_plan",
    "monitoring_report",
    "human_oversight",
    "appeals_flow",
    "soa",
    "policy_register",
    "audit_log"
}


@router.post("/systems/{system_id}/generate")
async def generate_system_documents(
    system_id: int,
    onboarding_data: Dict[str, Any] = Body(default=None),
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Generate all compliance documents for a system with real onboarding data."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Get system
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not system:
        # Debug: log all systems in the database
        all_systems = db.query(AISystem).all()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"System {system_id} not found for org {org.id}. Available systems: {[(s.id, s.name, s.org_id) for s in all_systems]}")
        raise HTTPException(status_code=404, detail="System not found")
    
    # FRIA gate: Check if FRIA is required and present
    if system.requires_fria:
        from app.models import Evidence
        
        # Check if FRIA evidence exists for this system
        fria_evidence = db.query(Evidence).filter(
            Evidence.system_id == system_id,
            Evidence.org_id == org.id,
            Evidence.label.ilike('%fria%')
        ).first()
        
        if not fria_evidence:
            raise HTTPException(
                status_code=409,
                detail=(
                    "FRIA (Fundamental Rights Impact Assessment) is required for this system "
                    "but has not been uploaded. Please complete the FRIA before generating documents."
                )
            )
    
    # Use provided onboarding data or fallback to defaults
    if not onboarding_data:
        onboarding_data = {
            "company": {
                "name": org.name,
                "address": "",
                "industry": ""
            },
            "risks": {
                "topRisks": [],
                "mitigationStrategies": []
            },
            "oversight": {
                "oversightRules": [],
                "escalationPaths": []
            },
            "monitoring": {
                "keyMetrics": [],
                "reviewFrequency": "Quarterly"
            }
        }
    
    try:
        # Normalize onboarding data structure
        if "systems" in onboarding_data and isinstance(onboarding_data["systems"], list):
            # Convert list to dict format expected by DocumentGenerator
            systems_dict = {}
            for i, system in enumerate(onboarding_data["systems"]):
                systems_dict[f"system_{i}"] = system
            onboarding_data["systems"] = systems_dict
        
        # Normalize risks data structure
        if "risks" in onboarding_data and isinstance(onboarding_data["risks"], list):
            # Convert list to dict format expected by DocumentGenerator
            onboarding_data["risks"] = {
                "topRisks": onboarding_data["risks"],
                "mitigationStrategies": []
            }
        
        generator = DocumentGenerator()
        generated_docs = generator.generate_all_documents(
            system_id=system_id,
            org_id=org.id,
            onboarding_data=onboarding_data,
            db=db
        )
        
        return {
            "system_id": system_id,
            "generated_documents": len(generated_docs),
            "documents": generated_docs,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")


@router.get("/systems/{system_id}/list")
async def list_system_documents(
    system_id: int,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """List all generated documents for a system."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Verify system exists and belongs to organization
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    try:
        generator = DocumentGenerator()
        documents = generator.get_document_list(system_id=system_id, org_id=org.id)
        
        return {
            "system_id": system_id,
            "documents": documents,
            "total_count": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/systems/{system_id}/download/{doc_type}")
async def download_document(
    system_id: int,
    doc_type: str,
    format: str = "markdown",
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Download a specific document for a system."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Validate document type
    if doc_type not in VALID_DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
    
    # Verify system exists and belongs to organization
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    if format not in ["markdown", "pdf"]:
        raise HTTPException(status_code=400, detail="Format must be 'markdown' or 'pdf'")
    
    try:
        generator = DocumentGenerator()
        content, actual_format = generator.get_document_content(
            system_id=system_id,
            org_id=org.id,
            doc_type=doc_type,
            format=format
        )
        
        # Determine content type and file extension based on actual format returned
        if actual_format == "markdown":
            media_type = "text/markdown"
            file_extension = "md"
        else:  # pdf
            media_type = "application/pdf"
            file_extension = "pdf"
        
        # Set filename
        filename = f"{doc_type}_{system.name.replace(' ', '_')}.{file_extension}"
        
        # Prepare headers
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        
        # Add fallback indicator if PDF was requested but markdown was returned
        if format == "pdf" and actual_format == "markdown":
            headers["X-PDF-Fallback"] = "WeasyPrint not available, returning markdown"
        
        return Response(
            content=content,
            media_type=media_type,
            headers=headers
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {doc_type} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/systems/{system_id}/preview/{doc_type}")
async def preview_document(
    system_id: int,
    doc_type: str,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Preview a document as HTML."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Validate document type
    if doc_type not in VALID_DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
    
    # Verify system exists and belongs to organization
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    try:
        generator = DocumentGenerator()
        content, actual_format = generator.get_document_content(
            system_id=system_id,
            org_id=org.id,
            doc_type=doc_type,
            format="markdown"
        )
        
        # Validate format before processing
        if actual_format != "markdown":
            raise HTTPException(status_code=500, detail=f"Preview only supports markdown format, got: {actual_format}")
        
        # Convert markdown to HTML
        import bleach
        import markdown
        
        html_content = markdown.markdown(
            content.decode('utf-8'),
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Sanitize HTML to prevent XSS attacks
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'strong', 'em', 'u', 'b', 'i',
            'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'a', 'img', 'div', 'span'
        ]
        
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'table': ['class'],
            'th': ['class'],
            'td': ['class'],
            'div': ['class'],
            'span': ['class']
        }
        
        html_content = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        # Wrap in HTML structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{doc_type.replace('_', ' ').title()} - {system.name}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    max-width: 1200px;
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
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return Response(content=full_html, media_type="text/html")
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {doc_type} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/templates")
async def list_available_templates(
    org: Organization = Depends(verify_api_key),
):
    """List all available document templates."""
    
    templates = [
        {
            "id": "risk_assessment",
            "name": "Risk Assessment",
            "description": "ISO/IEC 42001 clause 6.1 - Risk management plan",
            "iso_clauses": ["6.1", "Annex C"],
            "ai_act": ["Annex IV §6"]
        },
        {
            "id": "impact_assessment", 
            "name": "Impact Assessment",
            "description": "EU AI Act Annex IV - Impact assessment for high-risk AI systems",
            "iso_clauses": ["6.2"],
            "ai_act": ["Annex IV"]
        },
        {
            "id": "model_card",
            "name": "Model Card",
            "description": "Model documentation and transparency requirements",
            "iso_clauses": ["A.6.2", "B.6"],
            "ai_act": ["Annex IV §8"]
        },
        {
            "id": "data_sheet",
            "name": "Data Sheet",
            "description": "Dataset documentation and quality assessment",
            "iso_clauses": ["6.3"],
            "ai_act": ["Annex IV §7"]
        },
        {
            "id": "logging_plan",
            "name": "Logging Plan",
            "description": "System logging and audit trail requirements",
            "iso_clauses": ["7.1"],
            "ai_act": ["Annex IV §9"]
        },
        {
            "id": "monitoring_report",
            "name": "Monitoring Report",
            "description": "Performance monitoring and post-market surveillance",
            "iso_clauses": ["7.2"],
            "ai_act": ["Annex IV §10"]
        },
        {
            "id": "human_oversight",
            "name": "Human Oversight SOP",
            "description": "Human oversight procedures and escalation paths",
            "iso_clauses": ["6.4"],
            "ai_act": ["Annex IV §11"]
        },
        {
            "id": "appeals_flow",
            "name": "Appeals Flow",
            "description": "Appeals and redress procedures",
            "iso_clauses": ["6.5"],
            "ai_act": ["Annex IV §12"]
        },
        {
            "id": "soa",
            "name": "Statement of Applicability",
            "description": "ISO/IEC 42001 Statement of Applicability",
            "iso_clauses": ["4.2.3"],
            "ai_act": []
        },
        {
            "id": "policy_register",
            "name": "Policy Register",
            "description": "AI governance policies and procedures",
            "iso_clauses": ["5.2"],
            "ai_act": []
        },
        {
            "id": "audit_log",
            "name": "Audit Log",
            "description": "Audit trail and compliance monitoring",
            "iso_clauses": ["7.3"],
            "ai_act": ["Annex IV §13"]
        }
    ]
    
    return {
        "templates": templates,
        "total_count": len(templates)
    }
