from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.database import get_db
from datetime import datetime, timedelta, timezone
from fastapi.responses import StreamingResponse, RedirectResponse
from io import BytesIO
import zipfile

from app.models import AISystem, Organization, Control, Evidence, Incident, Action
from app.schemas import ReportSummary, ScoreResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
async def get_summary(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get summary report of AI systems."""
    try:
        # Get basic counts
        total_systems = db.query(AISystem).filter(AISystem.org_id == org.id).count()
        
        # Calculate evidence coverage with proper error handling
        evidence_coverage_pct = 0.0
        evidence_coverage_status = "unknown"
        
        try:
            # Use raw SQL to avoid SQLAlchemy trying to access non-existent columns
            from sqlalchemy import text
            
            # Count controls
            controls_result = db.execute(text("SELECT COUNT(*) FROM controls WHERE org_id = :org_id"), {"org_id": org.id})
            total_controls = controls_result.scalar()
            
            if total_controls > 0:
                # Count evidence with control_name (legacy approach)
                evidence_result = db.execute(
                    text("SELECT COUNT(*) FROM evidence WHERE org_id = :org_id AND control_name IS NOT NULL"), 
                    {"org_id": org.id}
                )
                evidence_count = evidence_result.scalar()
                
                # Count evidence with control_id (preferred approach)
                evidence_with_id_result = db.execute(
                    text("SELECT COUNT(*) FROM evidence WHERE org_id = :org_id AND control_id IS NOT NULL"), 
                    {"org_id": org.id}
                )
                evidence_with_id_count = evidence_with_id_result.scalar()
                
                # Use the better approach if available
                if evidence_with_id_count > 0:
                    evidence_coverage_pct = (evidence_with_id_count / total_controls) * 100
                    evidence_coverage_status = "calculated_with_id"
                elif evidence_count > 0:
                    evidence_coverage_pct = (evidence_count / total_controls) * 100
                    evidence_coverage_status = "calculated_legacy"
                else:
                    evidence_coverage_pct = 0.0
                    evidence_coverage_status = "no_evidence"
            else:
                evidence_coverage_status = "no_controls"
                print("INFO: No controls found for organization - evidence coverage set to 0%")
        except Exception as e:
            evidence_coverage_status = "error"
            print(f"ERROR: Could not calculate evidence coverage: {e}")
            evidence_coverage_pct = 0.0
        
        # Calculate real metrics - consider both criticality and ai_act_class
        high_risk_systems = db.query(AISystem).filter(
            AISystem.org_id == org.id,
            db.or_(
                AISystem.criticality == 'high',
                AISystem.ai_act_class == 'high-risk'
            )
        ).count()
        
        # Count incidents in last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        last_30d_incidents = db.query(Incident).filter(
            Incident.org_id == org.id,
            Incident.detected_at >= thirty_days_ago
        ).count()
        
        # Count GPAI systems
        gpai_count = db.query(AISystem).filter(
            AISystem.org_id == org.id,
            AISystem.is_general_purpose_ai == True
        ).count()
        
        # Count open actions in last 7 days
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        open_actions_7d = db.query(Action).filter(
            Action.org_id == org.id,
            Action.status.in_(['open', 'in_progress']),
            Action.created_at >= seven_days_ago
        ).count()
        
        return {
            "systems": total_systems,
            "high_risk": high_risk_systems,
            "last_30d_incidents": last_30d_incidents,
            "overrides_pct": None,
            "gpai_count": gpai_count,
            "evidence_coverage_pct": round(evidence_coverage_pct, 2),
            "evidence_coverage_status": evidence_coverage_status,
            "open_actions_7d": open_actions_7d,
        }
    except Exception as e:
        print(f"ERROR in get_summary: {e}")
        import traceback
        traceback.print_exc()
        # Return safe defaults
        return {
            "systems": 0,
            "high_risk": 0,
            "last_30d_incidents": 0,
            "overrides_pct": None,
            "gpai_count": 0,
            "evidence_coverage_pct": 0.0,
            "open_actions_7d": 0,
        }


@router.get("/score")
async def get_score(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    try:
        # Simple score calculation
        org_id = org.id
        
        # Get basic counts
        total_systems = db.query(AISystem).filter(AISystem.org_id == org_id).count()
        total_controls = db.query(Control).filter(Control.org_id == org_id).count()
        implemented_controls = db.query(Control).filter(
            Control.org_id == org_id, 
            Control.status == "implemented"
        ).count()
        
        # Calculate basic score
        if total_controls > 0:
            org_score = implemented_controls / total_controls
        else:
            org_score = 0.0
        
        # Get system scores
        systems = db.query(AISystem).filter(AISystem.org_id == org_id).all()
        system_scores = []
        
        for system in systems:
            system_controls = db.query(Control).filter(Control.system_id == system.id).count()
            system_implemented = db.query(Control).filter(
                Control.system_id == system.id,
                Control.status == "implemented"
            ).count()
            
            if system_controls > 0:
                system_score = system_implemented / system_controls
            else:
                system_score = 0.0
                
            system_scores.append({"id": system.id, "score": system_score})
        
        return {
            "org_score": org_score,
            "by_system": system_scores,
            "score_unit": "fraction",
            "tooltip": "Score based on implemented controls percentage",
            "coverage_pct": org_score * 100
        }
    except Exception as e:
        # Return basic data on error
        return {
            "org_score": 0.0,
            "by_system": [],
            "score_unit": "fraction",
            "tooltip": "Error calculating score",
            "coverage_pct": 0.0
        }


@router.get("/blocking-issues")
async def get_blocking_issues(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get real blocking issues preventing system deployment."""
    try:
        org_id = org.id
        blocking_issues = []
        
        # Check for high-risk systems
        high_risk_count = db.query(AISystem).filter(
            AISystem.org_id == org_id,
            AISystem.ai_act_class == "high"
        ).count()
        
        if high_risk_count > 0:
            blocking_issues.append({
                "id": "high-risk-systems",
                "type": "high_risk_detected",
                "severity": "critical",
                "title": f"{high_risk_count} high-risk system(s) detected",
                "description": "High-risk systems require additional compliance measures",
                "action": "Review high-risk systems",
                "action_url": "/inventory?filter=high-risk"
            })
        
        # Check for systems without evidence
        systems_without_evidence = db.query(AISystem).filter(
            AISystem.org_id == org_id
        ).all()
        
        for system in systems_without_evidence:
            evidence_count = db.query(Evidence).filter(
                Evidence.system_id == system.id
            ).count()
            
            if evidence_count == 0:
                blocking_issues.append({
                    "id": f"no-evidence-{system.id}",
                    "type": "evidence_missing",
                    "severity": "high",
                    "title": f"{system.name} has no evidence",
                    "description": "System requires compliance evidence before deployment",
                    "system_id": system.id,
                    "system_name": system.name,
                    "action": "Upload evidence",
                    "action_url": f"/systems/{system.id}/evidence"
                })
        
        return {"blocking_issues": blocking_issues}
        
    except Exception as e:
        # Return empty list on error to prevent frontend crashes
        return {"blocking_issues": []}


@router.get("/upcoming-deadlines")
async def get_upcoming_deadlines(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get real upcoming deadlines in the next 30 days."""
    try:
        org_id = org.id
        upcoming_deadlines = []
        
        # Get controls due in the next 30 days
        thirty_days_from_now = datetime.now(timezone.utc).date() + timedelta(days=30)
        
        controls_due = db.query(Control).filter(
            Control.org_id == org_id,
            Control.due_date.isnot(None),
            Control.due_date <= thirty_days_from_now,
            Control.status != "implemented"
        ).all()
        
        for control in controls_due:
            system = db.query(AISystem).filter(AISystem.id == control.system_id).first()
            if system:
                days_until_due = (control.due_date - datetime.now(timezone.utc).date()).days
                upcoming_deadlines.append({
                    "id": f"control-{control.id}",
                    "type": "control_deadline",
                    "title": f"{control.name}",
                    "description": f"Control due for {system.name}",
                    "due_date": control.due_date.isoformat(),
                    "days_until_due": days_until_due,
                    "system_id": system.id,
                    "system_name": system.name,
                    "action": "Complete control",
                    "action_url": f"/systems/{system.id}/controls"
                })
        
        return {"upcoming_deadlines": upcoming_deadlines}
        
    except Exception as e:
        # Return empty list on error to prevent frontend crashes
        return {"upcoming_deadlines": []}


@router.get("/annex-iv/{system_id}")
async def get_annex_iv_zip(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Generate Annex IV zip file for a system."""
    system = (
        db.query(AISystem)
        .filter(AISystem.id == system_id, AISystem.org_id == org.id)
        .first()
    )
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    # Create zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add system information
        system_info = f"""System ID: {system.id}
Name: {system.name}
Purpose: {system.purpose}
Domain: {system.domain}
Owner: {system.owner_email}
Deployment Context: {system.deployment_context}
Personal Data Processed: {system.personal_data_processed}
Impacts Fundamental Rights: {system.impacts_fundamental_rights}
AI Act Class: {system.ai_act_class}
Created: {system.id}
"""
        zip_file.writestr("system_info.txt", system_info)

        # Add controls
        controls = db.query(Control).filter(Control.system_id == system_id).all()
        for control in controls:
            control_info = f"""Control ID: {control.id}
Name: {control.name}
Status: {control.status}
Due Date: {control.due_date}
ISO Clause: {control.iso_clause}
Priority: {control.priority}
"""
            zip_file.writestr(f"controls/{control.id}.txt", control_info)

        # Add evidence
        evidence = db.query(Evidence).filter(Evidence.system_id == system_id).all()
        for ev in evidence:
            evidence_info = f"""Evidence ID: {ev.id}
Title: {ev.title}
Type: {ev.template_type}
Uploaded: {ev.uploaded_at}
File Size: {ev.file_size} bytes
"""
            zip_file.writestr(f"evidence/{ev.id}.txt", evidence_info)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=annex-iv-system-{system_id}.zip"}
    )