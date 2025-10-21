"""
Model Versions API

Endpoints for tracking model versions and change management.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, ModelVersion, Organization

router = APIRouter(prefix="/model-versions", tags=["model_versions"])


class CreateModelVersionRequest(BaseModel):
    version: str  # e.g., "1.0.0", "2.1.3"
    approver_email: EmailStr
    notes: str = None
    artifact_hash: str = None  # SHA-256 of model artifact


@router.post("/systems/{system_id}")
def create_model_version(
    system_id: int,
    payload: CreateModelVersionRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Create a new model version."""
    
    # Verify system exists
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Check if version already exists
    existing = (
        db.query(ModelVersion)
        .filter(
            ModelVersion.org_id == org.id,
            ModelVersion.system_id == system_id,
            ModelVersion.version == payload.version
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Version {payload.version} already exists for this system"
        )
    
    # Create version
    model_version = ModelVersion(
        org_id=org.id,
        system_id=system_id,
        version=payload.version,
        released_at=datetime.now(timezone.utc),
        approver_email=payload.approver_email,
        notes=payload.notes,
        artifact_hash=payload.artifact_hash
    )
    
    db.add(model_version)
    db.commit()
    db.refresh(model_version)
    
    return model_version


@router.get("/systems/{system_id}")
def list_model_versions(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all model versions for a system."""
    
    versions = (
        db.query(ModelVersion)
        .filter(
            ModelVersion.org_id == org.id,
            ModelVersion.system_id == system_id
        )
        .order_by(ModelVersion.released_at.desc())
        .all()
    )
    
    return versions


@router.get("/systems/{system_id}/latest")
def get_latest_model_version(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get the latest model version for a system."""
    
    version = (
        db.query(ModelVersion)
        .filter(
            ModelVersion.org_id == org.id,
            ModelVersion.system_id == system_id
        )
        .order_by(ModelVersion.released_at.desc())
        .first()
    )
    
    if not version:
        return {
            "version": "1.0.0",
            "released_at": None,
            "approver_email": None,
            "notes": "Initial version (no formal release recorded)"
        }
    
    return version
