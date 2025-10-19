import csv
import io
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import Control, Organization, AISystem, Evidence
from app.schemas import ControlBulkRequest

router = APIRouter(tags=["controls"])


@router.post("/bulk")
def bulk_upsert_controls(
    payload: ControlBulkRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    upserted = 0
    for item in payload.controls:
        # Convert Pydantic model to dict
        item_dict = item.model_dump() if hasattr(item, 'model_dump') else item
        
        system = (
            db.query(AISystem)
            .filter(AISystem.id == item_dict["system_id"], AISystem.org_id == org.id)
            .first()
        )
        if not system:
            raise HTTPException(status_code=404, detail=f"System {item_dict['system_id']} not found")

        ctrl = (
            db.query(Control)
            .filter(
                Control.org_id == org.id,
                Control.system_id == item_dict["system_id"],
                Control.iso_clause == item_dict["iso_clause"],
                Control.name == item_dict["name"],
            )
            .first()
        )
        if not ctrl:
            ctrl = Control(
                org_id=org.id,
                system_id=item_dict["system_id"],
                iso_clause=item_dict["iso_clause"],
                name=item_dict["name"],
            )
            db.add(ctrl)
        ctrl.priority = item_dict.get("priority") or "medium"
        ctrl.status = item_dict.get("status") or "missing"
        ctrl.owner_email = item_dict.get("owner_email")
        ctrl.rationale = item_dict.get("rationale")
        due = item_dict.get("due_date")
        ctrl.due_date = datetime.fromisoformat(due).date() if isinstance(due, str) and due else (due if hasattr(due, 'date') else None)
        ctrl.updated_at = datetime.now(timezone.utc)
        upserted += 1

    db.commit()
    return {"upserted": upserted}




def compute_evidence_coverage_pct(db: Session, org_id: int, system_id: int) -> float:
    controls = db.query(Control).filter(Control.org_id == org_id, Control.system_id == system_id).all()
    if not controls:
        return 0.0
    covered = 0
    for c in controls:
        match = (
            db.query(Evidence)
            .filter(
                Evidence.org_id == org_id,
                Evidence.system_id == system_id,
                ((Evidence.iso42001_clause == c.iso_clause) | (Evidence.control_name == c.name)),
            )
            .first()
        )
        if match:
            covered += 1
    return covered / len(controls)


