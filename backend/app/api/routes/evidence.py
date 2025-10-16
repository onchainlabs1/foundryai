from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, Evidence, Organization
from app.schemas import EvidenceResponse
from app.services.evidence import save_evidence_file
from app.services.text_extraction import ingest_evidence_text

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/view")
def get_evidence_viewer_metadata(
    evidence_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Get evidence metadata for PDF viewer deep linking.
    
    Returns file path, page count, checksum for viewer integration.
    Protected by API key, scoped to org.
    """
    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.org_id == org.id
    ).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    # Count pages from ArtifactText
    from app.models import ArtifactText
    pages_count = db.query(ArtifactText).filter(
        ArtifactText.evidence_id == evidence_id
    ).count()
    
    if pages_count == 0:
        pages_count = 1  # Assume at least 1 page if no artifacts yet
    
    return {
        "evidence_id": evidence.id,
        "label": evidence.label,
        "file_path": evidence.file_path,
        "checksum": evidence.checksum,
        "pages_count": pages_count,
        "iso42001_clause": evidence.iso42001_clause,
        "control_name": evidence.control_name,
        "created_at": evidence.created_at,
        "url": f"/viewer?evidence_id={evidence_id}&page=1"
    }


@router.post("/{system_id}", response_model=EvidenceResponse)
async def upload_evidence(
    system_id: int,
    file: UploadFile = File(...),
    label: str = None,
    iso42001_clause: str = None,
    control_name: str = None,
    version: str = None,
    uploaded_by: str = None,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Upload evidence file for an AI system."""
    # Verify system exists and belongs to org
    system = db.query(AISystem).filter(AISystem.id == system_id, AISystem.org_id == org.id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    # Default label to filename if not provided
    if not label:
        label = file.filename or "Uploaded Evidence"

    # Save file and get checksum
    file_path, checksum = await save_evidence_file(file, org.id, system_id)

    # Create evidence record
    evidence = Evidence(
        org_id=org.id,
        system_id=system_id,
        label=label,
        iso42001_clause=iso42001_clause,
        control_name=control_name,
        file_path=file_path,
        version=version,
        checksum=checksum,
        uploaded_by=uploaded_by,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    # Ingest text from PDF (async background task in production)
    try:
        ingest_evidence_text(db, evidence, file_path)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Warning: Text extraction failed for evidence {evidence.id}: {e}")

    return evidence

