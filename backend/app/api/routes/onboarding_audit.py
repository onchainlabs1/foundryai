"""
Audit-grade onboarding API endpoints.
EU AI Act + ISO/IEC 42001 compliance setup.
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AIRisk, AISystem, Control, Organization, Oversight, PMM
from app.schemas_audit import (
    ControlBulkCreate,
    ControlsBulkCreate,
    OrgSetup,
    OversightCreate,
    OversightResponse,
    PMMCreate,
    PMMResponse,
    RiskBulkCreate,
    RiskCreate,
    RiskResponse,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding-audit"])


@router.post("/org/setup")
async def setup_organization(
    setup_data: OrgSetup,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Update organization with audit-grade compliance contacts."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Update organization fields
    if setup_data.primary_contact_name:
        org.primary_contact_name = setup_data.primary_contact_name
    if setup_data.primary_contact_email:
        org.primary_contact_email = setup_data.primary_contact_email
    if setup_data.dpo_contact_name:
        org.dpo_contact_name = setup_data.dpo_contact_name
    if setup_data.dpo_contact_email:
        org.dpo_contact_email = setup_data.dpo_contact_email
    if setup_data.org_role:
        org.org_role = setup_data.org_role
    
    db.commit()
    db.refresh(org)
    
    return {
        "status": "success",
        "org_id": org.id,
        "message": "Organization setup updated"
    }


@router.post("/systems/{system_id}/risks/bulk", response_model=List[RiskResponse])
async def create_risks_bulk(
    system_id: int,
    bulk_data: RiskBulkCreate,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Create multiple risks for a system (minimum 3 required)."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Verify system exists and belongs to org
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Validate minimum 3 risks
    if len(bulk_data.risks) < 3:
        raise HTTPException(
            status_code=400,
            detail="Minimum 3 risks required for compliance"
        )
    
    # Delete existing risks for this system (replace all)
    db.query(AIRisk).filter(
        AIRisk.system_id == system_id,
        AIRisk.org_id == org.id
    ).delete()
    
    # Create new risks
    created_risks = []
    for risk_data in bulk_data.risks:
        db_risk = AIRisk(
            org_id=org.id,
            system_id=system_id,
            **risk_data.model_dump()
        )
        db.add(db_risk)
        created_risks.append(db_risk)
    
    db.commit()
    
    # Refresh all created risks
    for risk in created_risks:
        db.refresh(risk)
    
    return created_risks


@router.post("/controls/bulk")
async def create_controls_bulk(
    bulk_data: ControlsBulkCreate,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Create multiple controls in bulk."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    created_controls = []
    
    for control_data in bulk_data.controls:
        # Verify system exists and belongs to org
        system = db.query(AISystem).filter(
            AISystem.id == control_data.system_id,
            AISystem.org_id == org.id
        ).first()
        if not system:
            raise HTTPException(
                status_code=404,
                detail=f"System {control_data.system_id} not found"
            )
        
        # Create control
        db_control = Control(
            org_id=org.id,
            **control_data.model_dump()
        )
        db.add(db_control)
        created_controls.append(db_control)
    
    db.commit()
    
    # Refresh all created controls
    for control in created_controls:
        db.refresh(control)
    
    return {
        "status": "success",
        "count": len(created_controls),
        "message": "Controls created successfully. SoA draft updated."
    }


@router.post("/systems/{system_id}/oversight", response_model=OversightResponse)
async def create_oversight(
    system_id: int,
    oversight_data: OversightCreate,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Configure human oversight for an AI system (Art. 14/15)."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Verify system exists and belongs to org
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Check if oversight already exists (update) or create new
    existing = db.query(Oversight).filter(
        Oversight.system_id == system_id,
        Oversight.org_id == org.id
    ).first()
    
    if existing:
        # Update existing
        for key, value in oversight_data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        db_oversight = Oversight(
            org_id=org.id,
            system_id=system_id,
            **oversight_data.model_dump()
        )
        db.add(db_oversight)
        db.commit()
        db.refresh(db_oversight)
        return db_oversight


@router.post("/systems/{system_id}/pmm", response_model=PMMResponse)
async def create_pmm(
    system_id: int,
    pmm_data: PMMCreate,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Configure Post-Market Monitoring for an AI system (Art. 72)."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Verify system exists and belongs to org
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Check if PMM already exists (update) or create new
    existing = db.query(PMM).filter(
        PMM.system_id == system_id,
        PMM.org_id == org.id
    ).first()
    
    if existing:
        # Update existing
        for key, value in pmm_data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        db_pmm = PMM(
            org_id=org.id,
            system_id=system_id,
            **pmm_data.model_dump()
        )
        db.add(db_pmm)
        db.commit()
        db.refresh(db_pmm)
        return db_pmm


@router.get("/systems/{system_id}/risks", response_model=List[RiskResponse])
async def get_risks(
    system_id: int,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get all risks for a system."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Get risks
    risks = db.query(AIRisk).filter(
        AIRisk.system_id == system_id,
        AIRisk.org_id == org.id
    ).all()
    
    return risks


@router.get("/systems/{system_id}/oversight", response_model=OversightResponse)
async def get_oversight(
    system_id: int,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get oversight configuration for a system."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Get oversight
    oversight = db.query(Oversight).filter(
        Oversight.system_id == system_id,
        Oversight.org_id == org.id
    ).first()
    
    if not oversight:
        raise HTTPException(status_code=404, detail="Oversight configuration not found")
    
    return oversight


@router.get("/systems/{system_id}/pmm", response_model=PMMResponse)
async def get_pmm(
    system_id: int,
    x_api_key: str = Header(None),
    db: Session = Depends(get_db),
):
    """Get PMM configuration for a system."""
    
    # Verify API key and get organization
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    org = db.query(Organization).filter(Organization.api_key == x_api_key).first()
    if not org:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Get PMM
    pmm = db.query(PMM).filter(
        PMM.system_id == system_id,
        PMM.org_id == org.id
    ).first()
    
    if not pmm:
        raise HTTPException(status_code=404, detail="PMM configuration not found")
    
    return pmm

