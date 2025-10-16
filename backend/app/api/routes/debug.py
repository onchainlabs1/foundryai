"""
Debug endpoints for development and troubleshooting.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Organization, AISystem, Evidence, ArtifactText
from app.services.text_extraction import ingest_evidence_text

router = APIRouter(prefix="/debug", tags=["debug"])


class ReindexRequest(BaseModel):
    system_id: int


class ReindexResponse(BaseModel):
    system_id: int
    evidence_count: int
    inserted_count: int
    skipped_count: int
    errors: list


@router.post("/evidence/reindex", response_model=ReindexResponse)
def reindex_evidence(
    payload: ReindexRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Reindex all evidence for a system - extract text and populate ArtifactText.
    
    For each evidence file:
    - Open the file (PDF, TXT, etc.)
    - Extract text using PyMuPDF or plain read
    - Insert rows into artifact_text table
    
    Skips already-indexed evidence (checks for existing ArtifactText records).
    """
    system = db.query(AISystem).filter(
        AISystem.id == payload.system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Get all evidence for this system
    evidence_list = db.query(Evidence).filter(
        Evidence.system_id == payload.system_id,
        Evidence.org_id == org.id
    ).all()
    
    inserted_count = 0
    skipped_count = 0
    errors = []
    
    for evidence in evidence_list:
        # Check if already indexed
        existing = db.query(ArtifactText).filter(
            ArtifactText.evidence_id == evidence.id
        ).count()
        
        if existing > 0:
            skipped_count += 1
            continue
        
        # Ingest text from file
        try:
            count = ingest_evidence_text(db, evidence, evidence.file_path)
            inserted_count += count
        except Exception as e:
            errors.append({
                "evidence_id": evidence.id,
                "error": str(e)
            })
    
    return ReindexResponse(
        system_id=payload.system_id,
        evidence_count=len(evidence_list),
        inserted_count=inserted_count,
        skipped_count=skipped_count,
        errors=errors
    )


@router.get("/artifact_text")
def get_artifact_text_debug(
    system_id: int = None,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Debug endpoint to inspect ArtifactText records.
    
    Returns count and sample records for troubleshooting.
    """
    query = db.query(ArtifactText).filter(ArtifactText.org_id == org.id)
    
    if system_id:
        query = query.filter(ArtifactText.system_id == system_id)
    
    total_count = query.count()
    samples = query.limit(10).all()
    
    return {
        "count": total_count,
        "system_id": system_id,
        "samples": [
            {
                "id": sample.id,
                "evidence_id": sample.evidence_id,
                "page": sample.page,
                "iso_clause": sample.iso_clause,
                "ai_act_ref": sample.ai_act_ref,
                "content_preview": sample.content[:100] if sample.content else None,
                "checksum": sample.checksum[:16]
            }
            for sample in samples
        ]
    }

