from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
import hashlib
import os
from pathlib import Path

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
        "created_at": evidence.upload_date,
        "url": f"/viewer?evidence_id={evidence_id}&page=1"
    }


@router.post("/{system_id}", response_model=EvidenceResponse)
async def upload_evidence(
    system_id: int,
    file: UploadFile = File(None),
    content: str = Form(None),
    label: str = Form(None),
    iso42001_clause: str = Form(None),
    control_name: str = Form(None),
    version: str = Form(None),
    uploaded_by: str = Form(None),
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Upload evidence file or content for an AI system."""
    import logging
    from fastapi import HTTPException
    
    logger = logging.getLogger(__name__)
    
    # Verify system exists and belongs to org
    system = db.query(AISystem).filter(AISystem.id == system_id, AISystem.org_id == org.id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    # Handle either file upload or content
    if file and file.filename:
        # Security validations for file upload
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
        ALLOWED_MIME_TYPES = {
            'application/pdf',
            'text/plain',
            'text/markdown',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/jpeg',
            'image/png',
            'image/gif',
            'text/csv'
        }
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            logger.warning(f"File upload rejected: size {len(file_content)} exceeds limit {MAX_FILE_SIZE}")
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Check MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            logger.warning(f"File upload rejected: invalid MIME type {file.content_type}")
            raise HTTPException(status_code=415, detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}")
        
        # Reset file pointer for processing
        await file.seek(0)
        # Traditional file upload
        if not label:
            label = file.filename or "Uploaded Evidence"
        
        # Save file and get checksum
        file_path, checksum = await save_evidence_file(file, org.id, system_id)
        
    elif content:
        # Markdown content upload
        if not label:
            label = "Generated Evidence"
        
        # Create markdown file
        evidence_dir = Path(f"evidence/{org.id}/{system_id}")
        evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        import time
        timestamp = int(time.time())
        filename = f"evidence_{timestamp}.md"
        file_path = evidence_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Calculate checksum
        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
    else:
        raise HTTPException(status_code=400, detail="Either file or content must be provided")

    # Create evidence record
    evidence = Evidence(
        org_id=org.id,
        system_id=system_id,
        label=label,
        iso42001_clause=iso42001_clause,
        control_name=control_name,
        file_path=str(file_path),
        version=version,
        checksum=checksum,
        uploaded_by=uploaded_by,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    # Ingest text from file (async background task in production)
    try:
        ingest_evidence_text(db, evidence, str(file_path))
    except Exception as e:
        # Log error but don't fail the upload
        logger.warning(f"Text extraction failed for evidence {evidence.id}: {e}")

    return evidence

