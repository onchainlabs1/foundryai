"""
Compliance Suite API Routes - Template-based document generation endpoints.
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_api_key
from app.database import get_db
from app.models import Organization
from app.schemas import (
    ComplianceDraftRequest, ComplianceDraftResponse,
    DocumentSection, EvidenceCitation, RefineRequest, RefineResponse
)
from app.services.compliance_suite import compliance_suite_service
from app.services.s3 import s3_service

router = APIRouter(prefix="/reports", tags=["compliance-suite"])


@router.post("/draft", response_model=ComplianceDraftResponse)
def generate_compliance_draft(
    request: ComplianceDraftRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Generate draft compliance documents with evidence-grounded content.
    
    Returns documents with coverage metrics and missing sections.
    """
    try:
        result = compliance_suite_service.generate_draft_documents(
            db=db,
            org_id=org.id,
            system_id=request.system_id,
            doc_types=request.docs
        )
        
        return ComplianceDraftResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate compliance draft: {str(e)}"
        )


@router.get("/export/{doc_type}.{format}")
def export_compliance_document(
    doc_type: str,
    format: str,
    system_id: Optional[int] = Query(None),
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Export a compliance document in the specified format.
    
    Supported formats: md, docx, pdf
    Supported documents: annex_iv, fria, pmm, soa, risk_register
    """
    
    # Validate document type
    valid_docs = ["annex_iv", "fria", "pmm", "soa", "risk_register"]
    if doc_type not in valid_docs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Must be one of: {', '.join(valid_docs)}"
        )
    
    # Validate format
    valid_formats = ["md", "docx", "pdf"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        )
    
    # Check PDF export availability
    if format == "pdf" and not settings.ENABLE_PDF_EXPORT:
        raise HTTPException(
            status_code=424,
            detail="PDF export is disabled. Contact administrator."
        )
    
    try:
        filename, content_bytes = compliance_suite_service.export_document(
            db=db,
            org_id=org.id,
            system_id=system_id,
            doc_type=doc_type,
            format=format
        )
        
        # Determine content type
        content_types = {
            "md": "text/markdown",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf"
        }
        
        return StreamingResponse(
            io.BytesIO(content_bytes),
            media_type=content_types[format],
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Bundle-Hash": compliance_suite_service._generate_bundle_hash({}),
                "X-Generated-At": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export document: {str(e)}"
        )


@router.get("/evidence/view")
def view_evidence_page(
    evidence_id: int = Query(...),
    page: int = Query(1, ge=1),
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Get presigned URL or proxy link for viewing evidence at specific page.
    
    Returns URL for PDF.js viewer with page parameter.
    """
    from app.models import Evidence
    
    # Get evidence record
    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.org_id == org.id
    ).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    try:
        if settings.use_s3:
            # Generate presigned URL for S3 GET (viewing)
            s3_key = evidence.file_path
            presigned_url = s3_service.generate_presigned_get_url(
                key=s3_key,
                expires_in=settings.S3_URL_EXP_MIN * 60  # Convert minutes to seconds
            )
            
            # Add page parameter for PDF.js
            viewer_url = f"{presigned_url}#page={page}"
            
        else:
            # Local file - return relative path
            viewer_url = f"/evidence/view/{evidence_id}?page={page}"
        
        return {
            "evidence_id": evidence_id,
            "page": page,
            "viewer_url": viewer_url,
            "filename": evidence.label,  # Use label instead of non-existent filename
            "expires_in": settings.S3_URL_EXP_MIN * 60 if settings.use_s3 else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate evidence viewer URL: {str(e)}"
        )


@router.post("/refine", response_model=RefineResponse)
def refine_document_content(
    request: RefineRequest,
    org: Organization = Depends(verify_api_key),
):
    """
    Refine document content using LLM (feature-flagged).
    
    This endpoint is only available when FEATURE_LLM_REFINE=true.
    """
    
    if not settings.FEATURE_LLM_REFINE:
        raise HTTPException(
            status_code=403,
            detail="LLM refinement feature is disabled"
        )
    
    # TODO: Implement LLM refinement logic
    # For now, return the original content unchanged
    return RefineResponse(
        paragraphs=request.paragraphs,
        refined_at=datetime.now(timezone.utc).isoformat()
    )


@router.get("/export/soa.md")
def export_soa_narrative(
    system_id: Optional[int] = Query(None),
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Export narrative SoA from current CSV using template placeholders.
    
    This is a specialized endpoint for the SoA document.
    """
    try:
        filename, content_bytes = compliance_suite_service.export_document(
            db=db,
            org_id=org.id,
            system_id=system_id,
            doc_type="soa",
            format="md"
        )
        
        return StreamingResponse(
            io.BytesIO(content_bytes),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Generated-At": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export SoA narrative: {str(e)}"
        )


# Import io for StreamingResponse
import io
