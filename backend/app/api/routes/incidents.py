from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Incident, Organization, AISystem
from app.schemas import IncidentCreate

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("")
def create_incident(
    payload: IncidentCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    system = db.query(AISystem).filter(AISystem.id == payload.system_id, AISystem.org_id == org.id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    inc = Incident(
        org_id=org.id,
        system_id=payload.system_id,
        severity=payload.severity,
        description=payload.description,
        detected_at=payload.detected_at or datetime.now(timezone.utc),
        resolved_at=payload.resolved_at,
        corrective_action=payload.corrective_action,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)
    return inc


@router.get("")
def list_incidents(system_id: Optional[int] = None, org: Organization = Depends(verify_api_key), db: Session = Depends(get_db)):
    q = db.query(Incident).filter(Incident.org_id == org.id)
    if system_id is not None:
        q = q.filter(Incident.system_id == system_id)
    return q.order_by(Incident.detected_at.desc()).all()


@router.patch("/{incident_id}")
def update_incident(
    incident_id: int,
    payload: IncidentCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    inc = db.query(Incident).filter(Incident.id == incident_id, Incident.org_id == org.id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields from payload (exclude unset fields)
    update_data = payload.model_dump(exclude_unset=True, exclude={'system_id'})
    for field, value in update_data.items():
        setattr(inc, field, value)
    
    inc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(inc)
    return inc


