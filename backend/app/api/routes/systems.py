import csv
import io
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Response
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, Organization, Control
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


@router.get("/{system_id}", response_model=AISystemResponse)
async def get_system(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get a specific AI system by ID."""
    system = db.query(AISystem).filter(
        AISystem.id == system_id, 
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return system


@router.patch("/{system_id}", response_model=AISystemResponse)
async def patch_system(
    system_id: int,
    system_updates: dict,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Update specific fields of an existing AI system."""
    existing_system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not existing_system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Update only provided fields
    allowed_fields = {
        'name', 'purpose', 'domain', 'owner_email', 'uses_biometrics',
        'is_general_purpose_ai', 'impacts_fundamental_rights', 'personal_data_processed',
        'training_data_sensitivity', 'output_type', 'deployment_context',
        'criticality', 'notes'
    }
    
    for field, value in system_updates.items():
        if field in allowed_fields and hasattr(existing_system, field):
            setattr(existing_system, field, value)
    
    db.commit()
    db.refresh(existing_system)
    return existing_system


@router.put("/{system_id}", response_model=AISystemResponse)
async def update_system(
    system_id: int,
    system: AISystemCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Update an existing AI system (full replacement)."""
    existing_system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    
    if not existing_system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Update fields
    for field, value in system.dict(exclude_unset=True).items():
        setattr(existing_system, field, value)
    
    db.commit()
    db.refresh(existing_system)
    return existing_system


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


@router.get("/{system_id}/controls")
def list_controls(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Control)
        .filter(Control.system_id == system_id, Control.org_id == org.id)
        .order_by(Control.iso_clause)
        .all()
    )
    return items


@router.post("/{system_id}/onboarding-data")
@router.put("/{system_id}/onboarding-data")  # Alias for compatibility
async def save_onboarding_data(
    system_id: int,
    onboarding_data: dict,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Save onboarding data for a system."""
    from app.models import OnboardingData
    import json
    
    # Check if system exists and belongs to org
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Check if onboarding data already exists
    existing_data = db.query(OnboardingData).filter(
        OnboardingData.system_id == system_id,
        OnboardingData.org_id == org.id
    ).first()
    
    if existing_data:
        # Update existing data
        existing_data.data_json = json.dumps(onboarding_data)
        existing_data.updated_at = datetime.now(timezone.utc)
    else:
        # Create new data
        new_data = OnboardingData(
            org_id=org.id,
            system_id=system_id,
            data_json=json.dumps(onboarding_data)
        )
        db.add(new_data)
    
    db.commit()
    return {"status": "success", "message": "Onboarding data saved"}


@router.get("/{system_id}/onboarding-data")
async def get_onboarding_data(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get onboarding data for a system."""
    from app.models import OnboardingData
    import json
    
    # Check if system exists and belongs to org
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.org_id == org.id
    ).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    
    # Get onboarding data
    onboarding_data = db.query(OnboardingData).filter(
        OnboardingData.system_id == system_id,
        OnboardingData.org_id == org.id
    ).first()
    
    if not onboarding_data:
        return {"data": None}
    
    try:
        data = json.loads(onboarding_data.data_json)
        return {"data": data}
    except json.JSONDecodeError:
        return {"data": None}


@router.get("/{system_id}/soa.csv")
def export_soa_csv(system_id: int, org: Organization = Depends(verify_api_key), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["iso_clause", "applicable", "justification"])
    # MVP: applicable if there is at least one control mapped to clause; justification from rationale
    items = (
        db.query(Control)
        .filter(Control.system_id == system_id, Control.org_id == org.id)
        .order_by(Control.iso_clause)
        .all()
    )
    for c in items:
        writer.writerow([c.iso_clause or "", True, c.rationale or ""])
    return Response(content=output.getvalue(), media_type="text/csv")

