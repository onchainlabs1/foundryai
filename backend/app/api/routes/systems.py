import csv
import io
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, File, Header, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from app.models import AISystem, Control, Evidence, Organization
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
        'criticality', 'notes', 'lifecycle_stage', 'affected_users',
        'third_party_providers', 'risk_category', 'system_role',
        'processes_sensitive_data', 'uses_gpai', 'biometrics_in_public',
        'annex3_categories', 'impacted_groups'
    }
    
    for field, value in system_updates.items():
        if field in allowed_fields and hasattr(existing_system, field):
            setattr(existing_system, field, value)
    
    # Recompute requires_fria if relevant fields changed
    if any(field in system_updates for field in ['impacts_fundamental_rights', 'biometrics_in_public', 'annex3_categories']):
        from app.services.fria_logic import compute_requires_fria
        existing_system.requires_fria = compute_requires_fria(
            impacts_fundamental_rights=existing_system.impacts_fundamental_rights or False,
            biometrics_in_public=existing_system.biometrics_in_public or False,
            annex3_categories=existing_system.annex3_categories
        )
    
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
    
    # Ensure all required fields have default values
    system_data = system.model_dump()
    system_data.update({
        'impacts_fundamental_rights': system_data.get('impacts_fundamental_rights', False),
        'personal_data_processed': system_data.get('personal_data_processed', False),
        'uses_biometrics': system_data.get('uses_biometrics', False),
        'is_general_purpose_ai': system_data.get('is_general_purpose_ai', False),
        'processes_sensitive_data': system_data.get('processes_sensitive_data', False),
        'uses_gpai': system_data.get('uses_gpai', False),
        'biometrics_in_public': system_data.get('biometrics_in_public', False),
        'requires_fria': system_data.get('requires_fria', False),
    })
    
    db_system = AISystem(**system_data, org_id=org.id)

    # Auto-classify AI Act
    system_dict = system.model_dump()
    db_system.ai_act_class = classify_ai_act(system_dict)
    
    # Auto-compute requires_fria
    from app.services.fria_logic import compute_requires_fria
    db_system.requires_fria = compute_requires_fria(
        impacts_fundamental_rights=db_system.impacts_fundamental_rights or False,
        biometrics_in_public=db_system.biometrics_in_public or False,
        annex3_categories=db_system.annex3_categories
    )

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
    import json

    from app.models import OnboardingData
    
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
    import json

    from app.models import OnboardingData
    
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
    """Export Statement of Applicability as CSV with full audit trail."""
    from app.models import Evidence
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Enhanced header with all audit-grade columns
    writer.writerow([
        "ISO/IEC 42001 Clause",
        "Control Name",
        "Applicable",
        "Justification/Rationale",
        "Owner Email",
        "Implementation Status",
        "Due Date",
        "Evidence Links"
    ])
    
    # Get all controls for this system
    items = (
        db.query(Control)
        .filter(Control.system_id == system_id, Control.org_id == org.id)
        .order_by(Control.iso_clause)
        .all()
    )
    # Write control rows with evidence
    for control in items:
        # Get evidence for this control
        evidence_list = db.query(Evidence).filter(
            Evidence.control_id == control.id,
            Evidence.org_id == org.id
        ).all()
        
        evidence_links = ", ".join([
            f"{e.label} (v{e.version or '1'})" for e in evidence_list
        ]) if evidence_list else "No evidence uploaded"
        
        writer.writerow([
            control.iso_clause or "N/A",
            control.name,
            "Yes" if control.status != "missing" else "No",
            control.rationale or "N/A",
            control.owner_email or "Unassigned",
            control.status.upper(),
            control.due_date.isoformat() if control.due_date else "Not set",
            evidence_links
        ])
    
    return Response(content=output.getvalue(), media_type="text/csv")

