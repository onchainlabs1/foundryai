"""
Text extraction service for evidence documents using PyMuPDF.
Extracts text from PDFs and stores in ArtifactText for compliance suite.
"""
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from sqlalchemy.orm import Session

from app.models import ArtifactText, Evidence

# Mapping patterns for filename/label to ISO clause or AI Act reference
CLAUSE_PATTERNS = {
    r"risk.*assess": "ISO42001:6.1.1",
    r"data.*quality": "ISO42001:6.2.1",
    r"bias.*mitigat": "ISO42001:6.2.2",
    r"transparency": "AIAct:Art12",
    r"human.*oversight": "ISO42001:8.2.3",
    r"robustness": "ISO42001:8.2.4",
    r"technical.*doc": "AnnexIV.8",
    r"pmm|monitoring": "AIAct:Art72",
    r"fria|rights": "AIAct:Art27",
}


def infer_clause_from_filename(filename: str, label: str = "") -> tuple[Optional[str], Optional[str]]:
    """
    Infer ISO clause and AI Act reference from filename/label patterns.
    
    Returns:
        (iso_clause, ai_act_ref) tuple, both can be None
    """
    text = f"{filename} {label}".lower()
    
    for pattern, ref in CLAUSE_PATTERNS.items():
        if re.search(pattern, text):
            if ref.startswith("ISO"):
                return (ref, None)
            elif ref.startswith("AIAct") or ref.startswith("Annex"):
                return (None, ref)
    
    return (None, None)


def extract_text_from_pdf(file_path: str) -> List[dict]:
    """
    Extract text from PDF file using PyMuPDF.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of dicts with {page: int, content: str, checksum: str}
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) not available. Install with: pip install pymupdf")
    
    pages_data = []
    
    try:
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            # Skip empty pages
            if not text.strip():
                continue
            
            # Create checksum for this page's content
            checksum = hashlib.sha256(text.encode()).hexdigest()
            
            pages_data.append({
                "page": page_num + 1,  # 1-indexed
                "content": text.strip(),
                "checksum": checksum
            })
        
        doc.close()
        
    except Exception as e:
        # If extraction fails, return empty list (graceful degradation)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to extract text from {file_path}: {e}")
        return []
    
    return pages_data


def ingest_evidence_text(
    db: Session,
    evidence: Evidence,
    file_path: str
) -> int:
    """
    Extract text from evidence file and store in ArtifactText.
    
    Args:
        db: Database session
        evidence: Evidence record
        file_path: Path to evidence file
        
    Returns:
        Number of ArtifactText records created
    """
    # Check if already ingested (avoid duplicates)
    existing_count = db.query(ArtifactText).filter(
        ArtifactText.evidence_id == evidence.id
    ).count()
    
    if existing_count > 0:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Evidence {evidence.id} already ingested, skipping")
        return 0
    
    # Infer clause from filename/label
    iso_clause, ai_act_ref = infer_clause_from_filename(
        Path(file_path).name,
        evidence.label
    )
    
    # Extract text from PDF
    pages_data = extract_text_from_pdf(file_path)
    
    if not pages_data:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"No text extracted from {file_path}, creating placeholder")
        # Create placeholder for non-PDF or empty files
        pages_data = [{
            "page": 1,
            "content": f"[Binary file: {Path(file_path).name}]",
            "checksum": hashlib.sha256(b"placeholder").hexdigest()
        }]
    
    # Store in ArtifactText
    created_count = 0
    for page_data in pages_data:
        artifact = ArtifactText(
            org_id=evidence.org_id,
            system_id=evidence.system_id,
            evidence_id=evidence.id,
            file_path=file_path,
            page=page_data["page"],
            checksum=page_data["checksum"],
            iso_clause=iso_clause or evidence.iso42001_clause,
            ai_act_ref=ai_act_ref,
            lang="en",
            content=page_data["content"],
            created_at=datetime.now(timezone.utc)
        )
        db.add(artifact)
        created_count += 1
    
    db.commit()
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Ingested {created_count} pages from evidence {evidence.id}")
    return created_count


def search_artifact_text(
    db: Session,
    org_id: int,
    system_id: Optional[int] = None,
    iso_clause: Optional[str] = None,
    ai_act_ref: Optional[str] = None,
    search_term: Optional[str] = None,
    limit: int = 5
) -> List[ArtifactText]:
    """
    Search ArtifactText records with filters.
    
    Args:
        db: Database session
        org_id: Organization ID
        system_id: Optional AI system ID filter
        iso_clause: Optional ISO clause filter
        ai_act_ref: Optional AI Act reference filter
        search_term: Optional full-text search term
        limit: Maximum results to return
        
    Returns:
        List of matching ArtifactText records
    """
    query = db.query(ArtifactText).filter(ArtifactText.org_id == org_id)
    
    if system_id:
        query = query.filter(ArtifactText.system_id == system_id)
    
    if iso_clause:
        query = query.filter(ArtifactText.iso_clause == iso_clause)
    
    if ai_act_ref:
        query = query.filter(ArtifactText.ai_act_ref == ai_act_ref)
    
    if search_term:
        # Simple LIKE search for SQLite (for Postgres, use tsvector)
        query = query.filter(ArtifactText.content.like(f"%{search_term}%"))
    
    return query.limit(limit).all()

