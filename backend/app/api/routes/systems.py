import csv
import io
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, Organization
from app.schemas import AISystemCreate, AISystemResponse, AssessmentResponse
from app.services.gap import generate_control_plan, generate_gap
from app.services.risk import classify_ai_act, detect_role, is_gpai

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get("", response_model=List[AISystemResponse])
async def list_systems(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all AI systems for the organization."""
    systems = db.query(AISystem).filter(AISystem.org_id == org.id).all()
    return systems


@router.post("", response_model=AISystemResponse)
async def create_system(
    system: AISystemCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Create a new AI system."""
    db_system = AISystem(**system.model_dump(), org_id=org.id)

    # Auto-classify AI Act
    system_dict = system.model_dump()
    db_system.ai_act_class = classify_ai_act(system_dict)

    db.add(db_system)
    db.commit()
    db.refresh(db_system)
    return db_system


@router.post("/import")
async def import_systems(
    file: UploadFile = File(...),
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Import AI systems from CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = await file.read()
    csv_data = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(csv_data)

    imported = 0
    for row in reader:
        # Convert string booleans
        bool_fields = [
            "uses_biometrics",
            "is_general_purpose_ai",
            "impacts_fundamental_rights",
            "personal_data_processed",
        ]
        for field in bool_fields:
            if field in row:
                row[field] = row[field].lower() in ("true", "1", "yes")

        system_dict = {k: v for k, v in row.items() if v and k in AISystemCreate.model_fields}
        db_system = AISystem(**system_dict, org_id=org.id)
        db_system.ai_act_class = classify_ai_act(system_dict)

        db.add(db_system)
        imported += 1

    db.commit()
    return {"imported": imported}


@router.post("/{system_id}/assess", response_model=AssessmentResponse)
async def assess_system(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Assess AI system for AI Act classification and ISO 42001 gaps."""
    system = db.query(AISystem).filter(AISystem.id == system_id, AISystem.org_id == org.id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    system_dict = {
        "uses_biometrics": system.uses_biometrics,
        "is_general_purpose_ai": system.is_general_purpose_ai,
        "impacts_fundamental_rights": system.impacts_fundamental_rights,
        "deployment_context": system.deployment_context,
    }

    ai_act_class = classify_ai_act(system_dict)
    role = detect_role(system_dict)
    gpai_flag = is_gpai(system_dict)
    # simple rationale string for transparency
    rationale = (
        "Biometrics in public → high"
        if system.uses_biometrics and system.deployment_context == "public"
        else (
            "Impacts fundamental rights → high"
            if system.impacts_fundamental_rights
            else ("GPAI flagged, class limited → limited" if system.is_general_purpose_ai else "Default minimal")
        )
    )
    gap = generate_gap(ai_act_class)
    control_plan = generate_control_plan(ai_act_class)

    # Update system classification
    system.ai_act_class = ai_act_class
    db.commit()

    return {
        "ai_act_class": ai_act_class,
        "is_gpai": gpai_flag,
        "role": role,
        "rationale": rationale,
        "gap": gap,
        "control_plan": control_plan,
    }

