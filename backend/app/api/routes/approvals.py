"""
Document Approvals API

Endpoints for submitting and approving compliance documents.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, DocumentApproval, Organization

router = APIRouter(prefix="/approvals", tags=["approvals"])


class SubmitForReviewRequest(BaseModel):
    doc_type: str  # annex_iv|fria|soa|pmm|instructions_for_use
    submitted_by: EmailStr
    notes: str = None


class ApproveDocumentRequest(BaseModel):
    approver_email: EmailStr
    notes: str = None


class RejectDocumentRequest(BaseModel):
    approver_email: EmailStr
    rejection_reason: str
    notes: str = None


@router.post("/systems/{system_id}/documents/submit")
def submit_document_for_review(
    system_id: int,
    payload: SubmitForReviewRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Submit a document for review."""
    
    # Verify system exists
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Check if document exists (generated)
    doc_dir = Path(f"generated_documents/org_{org.id}/system_{system_id}")
    
    # Map doc_type to filename
    doc_filename_map = {
        "annex_iv": "annex_iv.md",
        "fria": "fria.md",
        "soa": "soa.md",
        "monitoring_report": "monitoring_report.md",
        "pmm": "monitoring_report.md",  # Alias
        "instructions_for_use": "instructions_for_use.md",
        "risk_assessment": "risk_assessment.md",
        "human_oversight": "human_oversight.md",
        "logging_plan": "logging_plan.md",
        "appeals_flow": "appeals_flow.md"
    }
    
    doc_filename = doc_filename_map.get(payload.doc_type)
    if not doc_filename:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type: {payload.doc_type}")
    
    doc_path = doc_dir / doc_filename
    
    # Calculate document hash if file exists
    document_hash = None
    if doc_path.exists():
        with open(doc_path, 'rb') as f:
            document_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Check if approval record exists
    existing = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system_id,
            DocumentApproval.doc_type == payload.doc_type
        )
        .first()
    )
    
    if existing:
        # Update existing
        existing.status = "submitted"
        existing.submitted_by = payload.submitted_by
        existing.submitted_at = datetime.now(timezone.utc)
        existing.notes = payload.notes
        existing.document_hash = document_hash
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        approval = DocumentApproval(
            org_id=org.id,
            system_id=system_id,
            doc_type=payload.doc_type,
            status="submitted",
            submitted_by=payload.submitted_by,
            submitted_at=datetime.now(timezone.utc),
            notes=payload.notes,
            document_hash=document_hash
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return approval


@router.post("/systems/{system_id}/documents/{doc_type}/approve")
def approve_document(
    system_id: int,
    doc_type: str,
    payload: ApproveDocumentRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Approve a submitted document."""
    
    # Get approval record
    approval = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system_id,
            DocumentApproval.doc_type == doc_type
        )
        .first()
    )
    
    if not approval:
        raise HTTPException(
            status_code=404, 
            detail=f"No submission found for {doc_type}. Document must be submitted before approval."
        )
    
    if approval.status != "submitted":
        raise HTTPException(
            status_code=400,
            detail=f"Document is in '{approval.status}' status. Only submitted documents can be approved."
        )
    
    # Approve
    approval.status = "approved"
    approval.approver_email = payload.approver_email
    approval.approved_at = datetime.now(timezone.utc)
    if payload.notes:
        approval.notes = (approval.notes or "") + f"\nApproval notes: {payload.notes}"
    approval.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(approval)
    return approval


@router.post("/systems/{system_id}/documents/{doc_type}/reject")
def reject_document(
    system_id: int,
    doc_type: str,
    payload: RejectDocumentRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Reject a submitted document."""
    
    approval = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system_id,
            DocumentApproval.doc_type == doc_type
        )
        .first()
    )
    
    if not approval:
        raise HTTPException(status_code=404, detail="No submission found")
    
    # Reject
    approval.status = "rejected"
    approval.approver_email = payload.approver_email
    approval.approved_at = datetime.now(timezone.utc)  # timestamp of rejection
    approval.rejection_reason = payload.rejection_reason
    if payload.notes:
        approval.notes = (approval.notes or "") + f"\nRejection notes: {payload.notes}"
    approval.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(approval)
    return approval


@router.get("/systems/{system_id}/documents/approvals")
def list_document_approvals(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all document approvals for a system."""
    
    approvals = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system_id
        )
        .order_by(DocumentApproval.doc_type)
        .all()
    )
    
    return approvals


@router.get("/systems/{system_id}/documents/{doc_type}/approval")
def get_document_approval(
    system_id: int,
    doc_type: str,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get approval status for a specific document."""
    
    approval = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.org_id == org.id,
            DocumentApproval.system_id == system_id,
            DocumentApproval.doc_type == doc_type
        )
        .first()
    )
    
    if not approval:
        # Return default draft status if no approval record
        return {
            "doc_type": doc_type,
            "status": "draft",
            "submitted_by": None,
            "submitted_at": None,
            "approver_email": None,
            "approved_at": None
        }
    
    return approval
