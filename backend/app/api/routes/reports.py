from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.core.security import verify_api_key
from app.database import get_db
from datetime import datetime, timedelta, timezone
from fastapi.responses import StreamingResponse, RedirectResponse
from io import BytesIO
import zipfile
import hashlib
import logging

from app.models import AISystem, Organization, Control, Evidence, Incident, Action
from app.schemas import ReportSummary, ScoreResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/deck.pptx")
async def export_executive_deck(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Export executive presentation deck (PPTX)."""
    # TODO: Implement PPTX generation
    raise HTTPException(
        status_code=501, 
        detail="PPTX export not yet implemented. Use individual document downloads instead."
    )


@router.get("/export/pptx")
async def export_pptx_redirect(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Redirect to deck.pptx endpoint."""
    # TODO: Implement PPTX generation
    raise HTTPException(
        status_code=501, 
        detail="PPTX export not yet implemented. Use individual document downloads instead."
    )


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
            # Use ORM queries instead of raw SQL for better type safety
            from app.models import Control, Evidence
            
            # Count controls using ORM
            total_controls = db.query(Control).filter(Control.org_id == org.id).count()
            
            if total_controls > 0:
                # Count evidence with control_id (preferred approach)
                evidence_with_control_id = db.query(Evidence).filter(
                    Evidence.org_id == org.id,
                    Evidence.control_id.isnot(None)
                ).count()
                
                # Count evidence with control_name (legacy approach)
                evidence_with_control_name = db.query(Evidence).filter(
                    Evidence.org_id == org.id,
                    Evidence.control_name.isnot(None)
                ).count()
                
                if evidence_with_control_id > 0:
                    evidence_coverage_pct = (evidence_with_control_id / total_controls) * 100
                    evidence_coverage_status = "calculated_with_id"
                    logger.info(f"Evidence coverage calculated using control_id: {evidence_coverage_pct:.2f}%")
                elif evidence_with_control_name > 0:
                    evidence_coverage_pct = (evidence_with_control_name / total_controls) * 100
                    evidence_coverage_status = "calculated_legacy"
                    logger.info(f"Evidence coverage calculated using control_name (legacy): {evidence_coverage_pct:.2f}%")
                else:
                    evidence_coverage_pct = 0.0
                    evidence_coverage_status = "no_evidence"
                    logger.info("No evidence found for organization")
            else:
                evidence_coverage_status = "no_controls"
                logger.info("No controls found for organization - evidence coverage set to 0%")
        except Exception as e:
            evidence_coverage_status = "error"
            logger.error(f"Could not calculate evidence coverage: {e}")
            evidence_coverage_pct = 0.0
        
        # Calculate real metrics - consider both criticality and ai_act_class
        high_risk_systems = db.query(AISystem).filter(
            AISystem.org_id == org.id,
            or_(
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
        logger.error(f"ERROR in get_summary: {e}", exc_info=True)
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
            AISystem.ai_act_class == "high-risk"
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
            system = db.query(AISystem).filter(
                AISystem.id == control.system_id,
                AISystem.org_id == org_id
            ).first()
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
    return await _generate_annex_iv_zip(system_id, org, db)


@router.get("/export/annex-iv.zip")
async def get_annex_iv_zip_alias(
    system_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Generate Annex IV zip file for a system (alias with .zip extension)."""
    return await _generate_annex_iv_zip(system_id, org, db)


async def _generate_annex_iv_zip(
    system_id: int,
    org: Organization,
    db: Session,
):
    """Internal function to generate Annex IV zip file."""
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

        # Add evidence (only if any exists)
        try:
            evidence = db.query(Evidence).filter(Evidence.system_id == system_id).all()
            for ev in evidence:
                evidence_info = f"""Evidence ID: {ev.id}
Label: {ev.label}
Control Name: {ev.control_name}
ISO Clause: {ev.iso42001_clause}
Uploaded: {ev.upload_date}
Status: {ev.status}
File Path: {ev.file_path}
Version: {ev.version}
Checksum: {ev.checksum}
Uploaded By: {ev.uploaded_by}
Reviewer: {ev.reviewer_email}
Link/Location: {ev.link_or_location}
"""
                zip_file.writestr(f"evidence/{ev.id}.txt", evidence_info)
        except Exception as e:
            logger.warning(f"Could not fetch evidence for system {system_id}: {e}")
            # Continue without evidence

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()
    
    # Calculate hash for integrity
    file_hash = hashlib.sha256(zip_content).hexdigest()
    
    return StreamingResponse(
        BytesIO(zip_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=annex-iv-system-{system_id}.zip",
            "X-File-Hash": f"sha256:{file_hash}",
            "X-File-Size": str(len(zip_content))
        }
    )